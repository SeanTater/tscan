import os
import cv2
import multiprocessing
import futures
import cli
import sys

try:
    from gi.repository import GExiv2 as exiv
except ImportError:
    print "GExiv2 is missing. Consider installing gir*-gexiv2* or the like"
    sys.exit()

class ImageMeta(object):
    def __init__(self, filename):
        self.filename = filename
        self._data = None
        self.exiv = exiv.Metadata(filename)
    
    @property
    def data(self):
        if self._data is None:
            self._data = cv2.imread(self.filename)
        return self._data
    
    @data.setter
    def data(self, data):
        self._data = data

class NameListSource(cli.Plugin):
    ''' Creates new ImageMetas from a list of filenames
    
        It doesn't process the filenames, they're passed on raw. '''
    def __init__(self, filenames):
        self.filenames = filenames
    
    def run(self):
        for filename in self.filenames:
            yield ImageMeta(filename)

class FileSink(cli.Plugin):
    ''' Takes ImageMetas and saves them to new files
        
        You can either pass one filename, or a pattern.
        Patterns take pythonic string interpolation:
        %(path_noext)s.jpg -> /path/to/file.jpg
        path_noext -> Path, with directory name, no extension
        ext -> file extension, with dot
        path -> the whole path, fstart to finish'''
    
    def __init__(self, output_pattern="%(path_noext)s_out%(ext)s"):
        self.output_pattern = output_pattern
    
    def run(self, meta):
        ''' Takes image (ImageMeta) and writes it to a file '''
        includes = {"path": meta.filename}
        includes["path_noext"], includes["ext"] = os.path.splitext(meta.filename) 
        output = self.output_pattern % includes
        # Write image data
        cv2.imwrite(output, meta.data)
        # Write image metadata
        new_image = exiv.Metadata(output)
        for key in meta.exiv:
            new_image[key] = meta.exiv[key]
        new_image.save_file()


class Progress(cli.Plugin):
    def run(self, meta):
        ''' Print progress information to the console '''
        print 'Processing "%s"' %meta.filename
        return meta

class Pipe(object):
    # Adding 1 for IO waiting
    max_workers = multiprocessing.cpu_count() + 1
    def __init__(self, source, *parts):
        self.source = source
        self.parts = parts
    
    def run(self):
        # Load workers
        with futures.ThreadPoolExecutor(max_workers=self.max_workers) as e:
            #f = []
            #for s in self.source.run():
            #    f.append( e.submit(self.worker, s) )
            #    f[-1].exception()
                
            for meta in e.map(self.worker, self.source.run()):
                pass
                # Yield in the future?? Could be useful.
        
        #for meta in self.source.run():
        #    self.worker(meta)
               
    def worker(self, item):
        for part in self.parts:
            item = part.run(item)
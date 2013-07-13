import os
import cv2
import multiprocessing
import futures
import cli

class ImageMeta(object):
    def __init__(self, filename):
        self.filename = filename
        self._data = None
    
    @property
    def data(self):
        if self._data is None:
            self._data = cv2.imread(self.filename)
        return self._data
    
    @data.setter
    def data(self, data):
        self._data = data

@cli.register
class NameListSource(object):
    ''' Creates new ImageMetas from a list of filenames
    
        It doesn't process the filenames, they're passed on raw. '''
    _args = [ dict(name='filenames', metavar='filename', nargs='+', help='Input filenames') ]
    _builtin = True
    
    def __init__(self, filenames):
        self.filenames = filenames
    
    def run(self):
        for filename in self.filenames:
            yield ImageMeta(filename)
            
@cli.register
class FileSink(object):
    ''' Takes ImageMetas and saves them to new files
        
        You can either pass one filename, or a pattern.
        Patterns take pythonic string interpolation:
        %(path_noext)s.jpg -> /path/to/file.jpg
        path_noext -> Path, with directory name, no extension
        ext -> file extension, with dot
        path -> the whole path, fstart to finish'''
    _args = [ dict(name='output_pattern', help='Output filename pattern') ]
    _builtin = True
    
    def __init__(self, output_pattern="%(path_noext)s_out%(ext)s"):
        self.output_pattern = output_pattern
    
    def run(self):
        # Only act when others request it
        pass
    
    def put(self, meta):
        ''' Takes image (ImageMeta) and writes it to a file '''
        includes = {"path": meta.filename}
        includes["path_noext"], includes["ext"] = os.path.splitext(meta.filename)
        output = self.output_pattern % includes
        return cv2.imwrite(output, meta.data)

class Pipe(object):
    # Adding 1 for IO waiting
    max_workers = multiprocessing.cpu_count() + 1
    def __init__(self, source, *parts):
        self.source = source
        self.parts = parts
    
    def run(self):
        # Load workers
        with futures.ThreadPoolExecutor(max_workers=self.max_workers) as e:
            for item in self.source.run():
                e.submit(self.worker, item)
               
    def worker(self, item):
        for part in self.parts:
            item = part.run(item)
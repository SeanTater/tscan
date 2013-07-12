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
        self.names = names
    
    def run(self):
        for filename in self.names:
            meta = ImageMeta(filename)
            sink.put(meta)
            
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
    
    def put(self, image):
        ''' Takes image (ImageMeta) and writes it to a file '''
        includes = {"path": item.filename}
        includes["path_noext"], includes["ext"] = os.path.splitext(item.filename)
        output = self.output_pattern % includes
        return cv2.imwrite(output, image.data)

class Pipe(object):
    # Adding 1 for IO waiting
    max_workers = multiprocessing.cpu_count() + 1
    def __init__(self, args, source, *parts):
        self.args = args
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
            

'''
class Sprocket(object):
    _args = []
    _kwargs = []
    # This has the unfortunate effect of rendering __init__.__doc__ useless
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    def _getarg(self, index):
        return self.args[index]
    def _setarg(self, index, value):
        self.args[index] = value
    def _getkwarg(self, name):
        return self.kwargs[name]
    def _setkwarg(self, name, value):
        self.kwargs[name] = value
    
    @classmethod
    def sprocket_argument(cls, **info):
        cls._args.append(info)
        return property(
            fget=lambda self: self._getarg(len(self.args)-1),
            fset=lambda self, value: self._setarg(len(self.args)-1, value)
        )
        
    
    @classmethod
    def sprocket_option(cls, **info):
        cls._kwargs.append(info)
        return property(
            fget=lambda self: self._getarg(info['name']),
            fset=lambda self, value: self._setarg(info['name'], value))
'''
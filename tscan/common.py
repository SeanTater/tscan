import os
import cv2
import threading
import multiprocessing
import Queue as queue
import futures

class ImageMeta(object):
    def __init__(self, filename):
        self.filename = filename
        self.data = None

class NameListSource(object):
    ''' Creates new ImageMetas from a list of filenames '''
    def __init__(self, names):
        self.names = names
    
    def run(self):
        for filename in self.names:
            meta = ImageMeta(filename)
            # TODO: Might be a bottleneck
            meta.data = imread(filename)
            sink.put(meta)
        

class FileSink(object):
    ''' Takes ImageMetas and saves them to new files
        based on their old filenames and a pattern '''
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
    max_workers = multiprocessing.cpu_count() + 2
    def __init__(self, args, source, *parts):
        self.args = args
        self.source = source
        self.parts = parts
    
    def run(self):
        # Load workers, adding 1 for IO waiting
        with futures.ThreadPoolExecutor(max_workers=self.max_workers) as e:
            for item in self.source(self.args).run():
                e.submit(self.worker, item)
    
    def worker(self, item):
        for part in self.parts:
            item = part(self.args).run(item)

class Sprocket(object):
    def __init__(self, args):
        self.args = args
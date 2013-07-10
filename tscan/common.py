import os
import cv2
import threading
import multiprocessing
import Queue as queue

class ImageMeta(object):
    def __init__(self, filename):
        self.filename = filename
        self.data = None

class NameListSource(object):
    ''' Creates new ImageMetas from a list of filenames '''
    def __init__(self, names, sink):
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
    def __init__(self, output_pattern):
        self.output_pattern = output_pattern or "%(path_noext)s_out%(ext)s"
    
    def put(self, image):
        ''' Takes image (ImageMeta) and writes it to a file '''
        includes = {"path": item.filename}
        includes["path_noext"], includes["ext"] = os.path.splitext(item.filename)
        output = self.output_pattern % includes
        return cv2.imwrite(output, image.data)

class Pipe(object):
    cpus = multiprocessing.cpu_count()
    
    def __init__(self, main, sink=None, args):
        self.main = main
        self.sink = sink
        self.args = args
        self.pending = queue.Queue(self.cpus) # Configurable?
        
    def put(self, item):
        '''Queue "item" for processing '''
        self.pending.put(item)
    
    def run(self):
        # Load workers, adding 1 for IO waiting
        for i in range(self.cpus+1):
            worker = Thread(target=self.worker)
            worker.daemon=True
            worker.start()

        self.pending.join()
    
    def worker(self):
        try:
            meta = self.pending.get()
            out = self.main(meta, self.args).run()
            self.sink.put(out)
        finally:
            self.pending.task_done()
            
class Filter(object):
    @classmethod
    def arguments(cls, parser):
        parser.add_argument("input", nargs='+', help='input filename[s]')
        parser.add_argument("output", nargs='?', default=None, help='output filename or pattern (if more than one input)')
        
    def __init__(self, meta, args):
        self.meta = meta
        self.image = self.meta.load()
        self.args = args
                
    def run(self):
        cpus = multiprocessing.cpu_count()
        q = queue.Queue(2*cpus)
        # Load workers, adding 1 for IO waiting
        for i in range(cpus+1):
            worker = cls(args, q)
            worker.daemon=True
            worker.start()

        for filename in args.input:
            q.put(ImageMeta(filename, output=args.output))
        q.join()

import os
import cv2
import threading
import multiprocessing
import Queue as queue
class ImageMeta(object):
    def __init__(self, filename, output=None):
        self.filename = filename
        self.output = output or "%(path_noext)s_out%(ext)s" 

    def load(self):
        im = cv2.imread(self.filename)        
        self.width, self.height, self.channels = im.shape
        self.sum = im.sum()
        self.size = im.size
        return im
    
    def save(self, image):
        includes = {"path": self.filename}
        includes["path_noext"], includes["ext"] = os.path.splitext(self.filename)
        output = self.output % includes
        return cv2.imwrite(output, image)
        
class Command(threading.Thread):
    '''
        All the commands subclass this
        It allows for generally transparent threading
        Threading makes sense in this case since Numpy and CV are outside the GIL
    '''
    def __init__(self, args, queue):
        threading.Thread.__init__(self)
        self.args = args
        self.queue = queue

    ''' 
        Run all associated threads (one by default)
    '''
    @classmethod
    def supervise(cls, args):
        cls(args, None).run()

class Filter(Command):
    @classmethod
    def arguments(cls, parser):
        parser.add_argument("input", nargs='+', help='input filename[s]')
        parser.add_argument("output", nargs='?', default=None, help='output filename or pattern (if more than one input)')
    
    def run(self):
        while True:
            try:
                self.meta = self.queue.get()
                self.run_one()
            finally:
                self.queue.task_done()
                print self.queue.qsize()

    @classmethod
    def supervise(cls, args):
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

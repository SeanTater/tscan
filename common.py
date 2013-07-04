import cv2
import threading
class Image(object):
    def __init__(self, array, filename=None):
        self.array = array
        self.width, self.height, self.channels = array.shape
        self.filename = filename
        self.sum = self.array.sum()
        self.size = self.array.size

    @staticmethod
    def load(filename):
        return Image(cv2.imread(filename), filename=filename)
    
    def save(self, filename=None):
        if not (filename or self.filename):
            raise ValueError, "Save has no filename"
        return cv2.imwrite(filename or self.filename, self.array)
        
class Command(threading.Thread):
    '''
        All the commands subclass this
        It allows for generally transparent threading
        Threading makes sense in this case since Numpy and CV are outside the GIL
    '''
    def __init__(self, args, queue):
        self.args = args
        self.queue = queue

    ''' 
        Run all associated threads (one by default)
    '''
    @classmethod
    def supervise(self, args):
        

class Filter(Command):
    @classmethod
    def arguments(cls, parser):
        parser.add_argument("inputs", help='input filename[s]')
        parser.add_argument("output", help='output filename or pattern (if more than one input)')
    
    def __call__(self):
        q = queue.Queue()
        for filename in self.args.inputs:
            q.put(filename)
        

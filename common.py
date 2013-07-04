import cv2
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
        
class Command(object):
    def __init__(self, args):
        self.args = args

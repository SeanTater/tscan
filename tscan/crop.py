from common import ImageMeta
import cv2
import math


# Oh Snap! Y then X?! Yes, that's life!
class Point(object):
    def __init__(self, y, x):
        self.y, self.x = y, x
    
    def __getitem__(self, i):
        return (self.y, self.x)[i]
    
    def almost(self, pt, precision=10):
        ''' Are these points almost equal? '''
        return max(abs(self.y - pt.y), abs(self.x - pt.x)) < precision
        

class Region(object):
    def __init__(self, start, stop):
        self.start, self.stop = start, stop
        if issubclass(self.start, dict):
            self.start = Point(**self.start)
        if issubclass(self.stop, dict):
            self.stop = Point(**self.stop)
    
    def almost(self, region, precision=10):
        ''' Are these regions almost equal? '''
        return (self.start.almost(region.start, precision)
            and self.stop.almost(region.stop, precision))
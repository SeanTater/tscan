from common import ImageMeta
import cv2
import math

# Oh Snap! Y then X?! Yes, that's life!
class Point(object):
    def __init__(self, y, x):
        self.y, self.x = y, x
    
    def __getitem__(self, i):
        ''' Treat point as a tuple '''
        return (self.y, self.x)[i]
    
    def __setitem__(self, i, v):
        ''' Unlike tuple, point is mutable '''
        if i:
            self.x = v
        else:
            self.y = v
    
    def distance(self, pt):
        return math.sqrt((self.y - pt.y)**2 + (self.x - pt.x)**2)
        

class Region(object):
    ''' A rectangle made from two Point()'s
        Naturally, they need to be opposite corners, and the convention is for
        start to be top-left and end bottom-right.'''
    def __init__(self, start, stop):
        self.start, self.stop = start, stop
    
    def __repr__(self):
        return "<Region ({start.y}, {start.x})->({stop.y}, {stop.x})>".format(
               start=self.start, stop=self.stop)
    
    def mean_distance(self, region):
        return (self.start.distance(region.start)
                + self.stop.distance(region.stop)) / 2
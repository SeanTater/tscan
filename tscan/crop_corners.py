from common import ImageMeta
import cv2
import numpy
# STUB

class CropCorners(object):
    """Crops by searching for the corners of a high contrast rectangle
        Fast, but inaccurate."""

    def run(self, meta):        
        tlc = self.get_tlc(meta)
        meta.data = self.get_max(tlc)
    
    def get_tlc(self, meta):
        se = numpy.array([
            [-1.0, -1.0],
            [-1.0,  3.0]])
        mini = cv2.resize(meta.data, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
        return cv2.filter2D(mini, -1, se)
    
    def get_max(self, corner_filtered):
        up = numpy.array([
            [-1.0],
            [ 1.0],
            [ 0.0]])
        down = numpy.array([
            [ 0.0],
            [ 1.0],
            [-1.0]])
        left = numpy.array([-1.0, 1.0,  0.0])
        right = numpy.array([0.0, 1.0, -1.0])
        
        upf = cv2.filter2D(corner_filtered, -1, up)
        downf = cv2.filter2D(corner_filtered, -1, down)
        leftf = cv2.filter2D(corner_filtered, -1, left)
        rightf = cv2.filter2D(corner_filtered, -1, right)
        return ((upf > 0) & (downf > 0)) & ((leftf > 0) & (rightf > 0))

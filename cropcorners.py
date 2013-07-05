from common import Filter, ImageMeta
import cv2
import numpy
class CropCorners(Filter):
    __description__ = "Crops out an image by searching for the corners of the print"
    def run_one(self):
        self.get_tlc()
        image = self.get_max()
        self.meta.save(image)
    
    def get_tlc(self):
        se = numpy.array([
            [-1.0, -1.0],
            [-1.0,  3.0]])
        mini = cv2.resize(self.image, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
        self.corners = cv2.filter2D(self.mini, -1, se)
    
    def get_max(self):
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
        
        upf = cv2.filter2D(self.corners, -1, up)
        downf = cv2.filter2D(self.corners, -1, down)
        leftf = cv2.filter2D(self.corners, -1, left)
        rightf = cv2.filter2D(self.corners, -1, right)
        return ((upf > 0) & (downf > 0)) & ((leftf > 0) & (rightf > 0))

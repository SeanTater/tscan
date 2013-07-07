from common import Filter, ImageMeta
import cv2
import numpy
import code
class CropGradient(Filter):
    __description__ = "Crops out an image by searching for the corners of the print"

    def run_one(self):        
        self.image = self.meta.load()
        # Signed, larger than char 64bit etc would work too
        self.signed_gray = self.image.sum(axis=2)
        
        deriv_2_at_0 = [] # this[axis] = masks
        for axis in [0, 1]:
            # Get derivatives
            deriv_1 = numpy.diff(self.signed_gray, axis=axis)
            deriv_2 = numpy.diff(deriv_1, axis=axis)            
            # Now look for the pixels nearest to 0
            deriv_2_prev = numpy.roll(deriv_2, 1, axis=axis)
            deriv_2_next = numpy.roll(deriv_2, -1, axis=axis)
            deriv_2_at_0.append((deriv_2 <= deriv_2_prev) & (deriv_2 < deriv_2_next))
        
        code.interact(local=vars())
        
        self.meta.save(self.image)

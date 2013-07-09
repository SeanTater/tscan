from common import Filter
from crop import Region, Point
import numpy
class CropGradient(Filter):
    ''' Crops out an image using lines of strongest gradient
        
        This method of cropping:
            is very fast
            works only for rectangular images (cuts others incorrectly)
            needs the image to be very close to level
    '''

    def run_one(self):
        self.estimate()
        self.apply_crop()
    
    def estimate(self):
        image = self.meta.load()
        signed_gray = image.sum(axis=2)
        
        region = Region(Point(0, 0), Point(0, 0))
        for axis in [0, 1]:
            signed_axis = signed_gray.sum(axis=axis)
            # Get derivatives
            deriv_1 = numpy.diff(signed_axis)
            deriv_2 = numpy.diff(deriv_1)            
            # Now look for the pixels nearest to 0
            deriv_2_prev = numpy.roll(deriv_2, 1)
            deriv_2_next = numpy.roll(deriv_2, -1)
            deriv_2_at_0 = (deriv_2 <= deriv_2_prev) & (deriv_2 < deriv_2_next)
            deriv_2_at_0_i = numpy.flatnonzero(deriv_2_at_0)
            # Now pick the best start and stop
            # Add one because each deriv is off by 1/2                          
            start_ii = numpy.argmax(deriv_1[deriv_2_at_0_i]) + 1
            stop_ii = numpy.argmin(deriv_1[deriv_2_at_0_i]) + 1
            
            region.start[axis] = deriv_2_at_0_i[start_ii]
            region.stop[axis] = deriv_2_at_0_i[stop_ii]
            if region.start[axis] > region.stop[axis]:
                region.start[axis], region.stop[axis] = region.stop[axis], region.start[axis]
	return region

    def apply_crop(self, region):
        cropped_image = image[region.start.y:region.stop.y, region.start.x:region.stop.x]
        self.meta.save(cropped_image)

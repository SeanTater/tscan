import numpy
import scipy.ndimage
import cv2
import cli
import code

@cli.Plugin.register
class Destripe(cli.Plugin):
    ''' Looks for out-of-place vertical or horizontal lines and inpaints them
        '''
    _args = []
    _name = 'destripe'
    
    def neighbor_threshold(self, image, low=5, high=5):
        ''' Search for one pixel wide anomalies on the first axis
            Think of every line like this:
             A B C
            abs(A-C) is low
            abs(A-B) is high
            abs(C-B) is high
        '''
        image = numpy.array(image, dtype=numpy.int16)
        neighbor1_diff = scipy.ndimage.filters.convolve1d(image, [-1, 2, -1], axis=0)
        neighbor2_diff = scipy.ndimage.filters.convolve1d(image, [ 1, 0, -1], axis=0)
        noise =  numpy.abs(neighbor1_diff) > high
        noise &= numpy.abs(neighbor2_diff) < low
        noise =  noise.sum(axis=2) > 0 # Don't triple count colors
        noise =  noise.sum(axis=1)
        return noise
    
    def noise_threshold(self, shape, noise, threshold=0.5):
        ''' Threshold the sum of noise on a line according to a percentage of
            the other dimension. Note that the color images are multiplied'''
        return numpy.array(noise, dtype=float) / shape[1] > threshold
    
    def noise_mask(self, image):
        # This change isn't permanent, it's local to this function
        image = cv2.cvtColor(image, cv2.cv.CV_BGR2HSV)
        iroll = numpy.swapaxes(image, 0, 1)
        y_stripes = self.neighbor_threshold(image)
        x_stripes = self.neighbor_threshold(iroll)
        
        y_stripes = self.noise_threshold(image.shape, y_stripes)
        x_stripes = self.noise_threshold(iroll.shape, x_stripes)
        y_stripes, x_stripes = numpy.meshgrid(x_stripes, y_stripes)
        return y_stripes | x_stripes
    
    def run(self, meta):
        mask = self.noise_mask(meta.data)
        code.interact(local=vars())
        # Inpaint radius = 3, acceptable?
        cv2.inpaint(meta.data, numpy.array(mask, dtype=numpy.uint8), 3,
                    cv2.INPAINT_NS)
        return meta
    
'''      V1    
        mask = numpy.zeros(meta.data.shape[:-1], dtype=numpy.uint8)
        fix_lines = [None, None]
        for axis in [0, 1]:
            # It's easier to move the axes than to try to slice it
            image = numpy.rollaxis(meta.data, axis)
            a_minus_c = numpy.abs(image[:-2] - image[2:]) # indexes A's
            a_minus_b = numpy.abs(image[:-1] - image[1:])[:-1] # indexes A's
            
            # Select affected pixels
            fix_pixels = (a_minus_c < low) & (a_minus_b > high)
            # Now sum the bools in lines, apply a threshold, index B's
            pixel_threshold = image.shape[0] / 4 # n/?   ?=a guess 
            fix_lines[axis] = fix_pixels.sum(axis=2).sum(axis=1)
            fix_lines[axis] = numpy.flatnonzero(fix_lines[axis] > pixel_threshold) + 1
            
        # Paint it on the mask
        mask[fix_lines[0]] = 1
        mask[:, fix_lines[1]] = 1
'''
import numpy
import scipy.ndimage
import scipy.signal
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
    
    def noise_threshold(self, noise, z=2):
        ''' Pick out lines whose scores are more than z stdev from the local
            width-5 median'''
        local_median = scipy.signal.medfilt(noise, kernel_size=5)
        return numpy.abs(noise - local_median) > z*numpy.std(noise)
    
    def noise_mask(self, image, low=5, high=5, threshold=0.5):
        # This change isn't permanent, it's local to this function
        image = cv2.cvtColor(image, cv2.cv.CV_BGR2HSV)
        iroll = numpy.swapaxes(image, 0, 1)
        y_stripes = self.neighbor_threshold(image)
        x_stripes = self.neighbor_threshold(iroll)
        
        y_stripes = self.noise_threshold(y_stripes)
        x_stripes = self.noise_threshold(x_stripes)
        #code.interact(local=vars())
        y_stripes, x_stripes = numpy.meshgrid(x_stripes, y_stripes)
        return y_stripes | x_stripes
    
    def run(self, meta):
        mask = self.noise_mask(meta.data)
        # Inpaint radius = 3, acceptable?
        cv2.inpaint(meta.data, numpy.array(mask, dtype=numpy.uint8), 3,
                    cv2.INPAINT_NS)
        return meta

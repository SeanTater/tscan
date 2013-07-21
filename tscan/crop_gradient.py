from crop import Region, Point
import numpy
import cli
import code
import cv2
import numpy

@cli.Plugin.register
class CropGradient(cli.Plugin):
    ''' Crops out an image using lines of strongest gradient
        
        This method of cropping
            is fast,
            works only for rectangular images (cuts others incorrectly),
            and needs the image to be very close to level.
    '''
    _name = 'crop_gradient'
    _args = []
    def run(self, meta):
        region = self.estimate(meta)
        meta.data = meta.data[region.start.y:region.stop.y, region.start.x:region.stop.x]
        return meta
    #
    # Score: Take image data (as in ImageMeta().data) and yield two 1d arrays
    #        relating to probability that the line contains a relevant edge
    #
    def score_deriv(self, idata):
        idata = numpy.array(idata, dtype=numpy.int16)
        for axis in [0, 1]:
            # Color derivative
            deriv = numpy.diff(idata, axis=axis)
            # One dimension, absolute
            deriv = numpy.abs(deriv.sum(axis=2).sum(axis=int(not axis)))
            yield deriv
    
    def score_canny(self, idata):
        # Percentile is really slow (~1s runtime for a usual image)
        # Since this is a heuristic anyway, just base it on a 1% sample
        # 101 -> prime is better to avoid hatching
        sample=idata.flatten()[::101]
        low = numpy.percentile(sample, 10)
        high = numpy.percentile(sample, 90)
        imc = cv2.Canny(idata, low, high)
        for axis in [0, 1]:
            yield imc.sum(axis=axis)
    
    #
    # Local max: Search for local maxima, prepare for cutting regions
    #
    
    def local_max_1d(self, impulse):
        ''' Do a simple immediate-neighbor local maximum check.
            impulse: any 1D numpy array
            returns:
                2D array of (index into impulse, impulse[index]) sorted by
                impulse[index] '''
        maxima = (impulse[1:-1] > impulse[2:]) & (impulse[1:-1] > impulse[:-2])
        maxima = numpy.flatnonzero(maxima) + 1
        
        # Sort local maxima
        maxima = maxima[impulse[maxima].argsort()]
        
        return numpy.column_stack((maxima, impulse[maxima]))
    
    #
    # Region: Take impulses and maxima, generating an optimal crop region
    #
    
    def region_impulse(self, y_maxima, x_maxima):
        ''' Use the top two results in each axis to generate a cropping region 
            y_maxima: (index, impulse[index]) of greatest impulse, sorted
            x_maxima: same as y_maxima, can be a different length '''
        region = Region(Point(0, 0), Point(0, 0))
        for axis, maxima in enumerate([y_maxima, x_maxima]): 
            region.start[axis] = maxima[-1,0]
            region.stop[axis] = maxima[-2,0]
            if region.start[axis] > region.stop[axis]:
                region.start[axis], region.stop[axis] = region.stop[axis], region.start[axis]
        return region
    
    def estimate(self, meta):
        ''' Generate an estimated crop region given an ImageMeta '''
        axes = tuple(self.score_canny(meta.data))
        maxima = [self.local_max_1d(axis) for axis in axes]
        region = self.region_impulse(maxima[0], maxima[1])
        return region

''' Version 2
        signed_color = cv2.GaussianBlur(meta.data, (11, 11), 0) 
        signed_color = numpy.array(signed_color, dtype=numpy.int16)
        
        region = Region(Point(0, 0), Point(0, 0))
        for axis in [0, 1]:
            # Get derivatives
            deriv = numpy.diff(signed_color, axis=axis)
            # One dimension, absolute
            deriv = numpy.abs(deriv.sum(axis=2).sum(axis=int(not axis)))
            # Non maximal surpression
            deriv_prev = numpy.roll(deriv, 1)
            deriv_next = numpy.roll(deriv, -1)
            deriv_max = (deriv >= deriv_prev) & (deriv > deriv_next)
            deriv_max_i = numpy.flatnonzero(deriv_max) # indexes into deriv_max
            # Choose the best ones - this should be a pretty small list
            best_derivs_ii = deriv[deriv_max].argsort() # indexes into deriv_max_i
            region.start[axis] = deriv_max_i[best_derivs_ii[-1]]
            region.stop[axis] = deriv_max_i[best_derivs_ii[-2]]
            if region.start[axis] > region.stop[axis]:
                region.start[axis], region.stop[axis] = region.stop[axis], region.start[axis]
        return region
'''

''' Version 1
# Get derivatives
            deriv_1 = numpy.diff(signed_color, axis=axis).sum(axis=2).sum(axis=int(not axis))
            # Smooth
            #cs = deriv_1.cumsum()
            #cs = cs - numpy.roll(cs, 10)
            deriv_2 = numpy.diff(deriv_1)
            code.interact(local=vars())
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
'''
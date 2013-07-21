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
    
    def score_deriv(self, idata):
        ''' Estimate likelihood of an edge by taking directional derivatives
            idata: ImageMeta().data
            yields: 1d integer numpy array for each axis, y then x
        '''
        idata = numpy.array(idata, dtype=numpy.int16)
        for axis in [0, 1]:
            # Color derivative
            deriv = numpy.diff(idata, axis=axis)
            # One dimension, absolute
            deriv = numpy.abs(deriv.sum(axis=2).sum(axis=int(not axis)))
            yield deriv
    
    def score_canny(self, idata):
        ''' Estimate likelihood of an edge by summing Canny edge response.
            idata: ImageMeta().data
            yields: 1d integer numpy array for each axis, y then x
        '''
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
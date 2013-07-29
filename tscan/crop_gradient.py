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
        maxima = maxima[impulse[maxima].argsort()[::-1]]
        
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
            region.start[axis] = maxima[0,0]
            region.stop[axis] = maxima[1,0]
            if region.start[axis] > region.stop[axis]:
                region.start[axis], region.stop[axis] = region.stop[axis], region.start[axis]
        return region
    
    def combine(self, a, b):
        ''' Generate the unique combinations of a and b's cartesian product '''
        pass
    
    def region_aspect(self, y_maxima, x_maxima):
        ''' Choose the best region to cut based on aspect ratio and area
            y_maxima: (index, impulse[index]) of greatest impulse, sorted
            x_maxima: same as y_maxima, can be a different length '''
        TOP_N = 10
        top_x = min(TOP_N, len(x_maxima))
        top_y = min(TOP_N, len(y_maxima))
        bscore = 0
        bsy = bey = bsx = bex = 0
        
        # Generate combinations of y's and x's
        for syi in range(top_y):
            for eyi in range(syi+1, top_y):
                for sxi in range(top_x):
                    for exi in range(sxi+1, top_x):
                        sy, sy_impulse = y_maxima[syi]
                        ey, ey_impulse = y_maxima[eyi]
                        if sy > ey:
                            sy, sy_impulse, ey, ey_impulse = ey, ey_impulse, sy, sy_impulse
                        sx, sx_impulse = x_maxima[sxi]
                        ex, ex_impulse = x_maxima[exi]
                        if sx > ex:
                            sx, sx_impulse, ex, ex_impulse = ex, ex_impulse, sx, sx_impulse
                        
                        h, w = ey-sy, ex-sx
                        impulse = sy_impulse + sx_impulse + ey_impulse + ex_impulse
                        aspect = min(h, w) / max(h, w)
                        
                        area = h*w
                        
                        #print "a %i, i %i" %(area, impulse)
                        
                        score = area * impulse
                        if score > bscore:
                            bscore = score
                            bsy, bey, bsx, bex = sy, ey, sx, ex
        
        return Region(Point(bsy, bsx), Point(bey, bex))
    
    def estimate(self, meta):
        ''' Generate an estimated crop region given an ImageMeta '''
        axes = tuple(self.score_canny(meta.data))
        maxima = [self.local_max_1d(axis) for axis in axes]
        region = self.region_aspect(maxima[0], maxima[1])
        return region

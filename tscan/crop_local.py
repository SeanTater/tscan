from crop import Region, Point
import numpy
import cli
import code
import cv2
import os
from scipy import ndimage as scind

@cli.Plugin.register
class CropLocal(cli.Plugin):
    ''' Crops out an image by looking for a single region of low uniformity
        
        This method of cropping
            is moderately slow,
            works only for rectangular images (cuts others incorrectly),
            and needs the image to be very close to level.
    '''
    _name = 'crop_local'
    _args = []
    def run(self, meta):
        region = self.estimate(meta)
        meta.data = meta.data[region.start.y:region.stop.y, region.start.x:region.stop.x]
        return meta
    
    #
    # Score: Take image data (as in ImageMeta().data) and yield two 1d arrays
    #        relating to the axial contrast on the line
    
    def score_gauss(self, idata):
        ''' Find the difference between a point and its gaussian
            idata: ImageMeta().data
            yields: 1d integer numpy array for each axis, y then x
        '''
        
        idata = cv2.cvtColor(idata, cv2.cv.CV_BGR2Lab)
        big = numpy.array(cv2.blur(idata, (11, 11)), dtype=numpy.int16)
        little = numpy.array(cv2.blur(idata, (3, 3)), dtype=numpy.int16)
        #idata = numpy.array(idata, dtype=numpy.int16) # handle subtract
        for axis in [1, 0]:
            # The sum is purpendicular to the axis of interest
            impulse = numpy.abs(little - big).sum(axis=2).sum(axis=axis)
            yield scind.median_filter(impulse, 15)
            #yield impulse
    
    #
    # Local max: Search for local maxima, prepare for cutting regions
    #
    
    def otsu(self, impulse):
        ''' One dimensional otsu threshold
            impulse: any 1D numpy array
            returns:
                threshold'''
        # Pre-otsu: make a histogram
        #
        count, edge = numpy.histogram(impulse, 250)
        count = numpy.array(count, dtype=int)
        edge = numpy.array(edge[1:], dtype=int)
        # Trim to the bottom 90% (avoid the photo edges)
        count[-25:] = 0
        
        # Otsu (easier to vectorize with a histogram)
        #
        weight = count * edge
        weight_under = weight.cumsum()

        count_under = count.cumsum()
        count_over = count_under[-1] - count_under

        mean_under = weight_under / count_under
        mean_over = weight_under[-1] - weight_under / count_over

        otsu = count_under * count_over * (mean_under - mean_over)**2
        return edge[numpy.argmax(otsu)]
    
    #
    # Region: Take impulses and maxima, generating an optimal crop region
    #
    def region(self, sy, oy, sx, ox):
        # Find the first and last entry that passes the threshold in each axis
        y_threshold = numpy.flatnonzero(sy > oy)
        x_threshold = numpy.flatnonzero(sx > ox)
        return Region(
            Point(y_threshold[0], x_threshold[0]),
            Point(y_threshold[-1], x_threshold[-1]))
    
    def estimate(self, meta):
        ''' Generate an estimated crop region given an ImageMeta '''
        axes = tuple(self.score_gauss(meta.data))
        otsu = [self.otsu(axis) for axis in axes]
        region = self.region(axes[0], otsu[0], axes[1], otsu[1])
        return region

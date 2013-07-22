import unittest
import numpy
import cv2
from mock import Mock
from common import ImageMeta
from crop_gradient import CropGradient
from crop import Region, Point
import crop_log
import tscantest

class CropGradientTest(unittest.TestCase):
    def setUp(self):
        self.crop_gradient = CropGradient()
        self.meta = tscantest.metas[0]

    #
    # Overall
    #

    def test_one(self): 
        self.crop_gradient.run(self.meta)
        
        # Bug: returned bool output, should still be uint8
        self.assertEqual(self.meta.data.dtype, numpy.uint8) 

    def test_against_reference(self):
        distance = []
        for meta in tscantest.metas:
            region = self.crop_gradient.estimate(meta)
            print region
            md = region.mean_distance(meta.reference_crop)
            distance.append(md)
            crop_log.default.dump(method='gradient',
                         generated=region, sample=meta)
        
        # It has to work on average
        assert sum(distance)/len(distance) < 50

    #
    # Score
    #
    
    def sub_test_score(self, method):
        for result in method(tscantest.metas[0].data):
            assert isinstance(result, numpy.ndarray)
            assert result.ndim == 1

    def test_score_deriv(self):
        self.sub_test_score(self.crop_gradient.score_deriv)

    def test_score_canny(self):
        self.sub_test_score(self.crop_gradient.score_canny)

    def test_local_max_1d(self):
        # Handle a real situation
        sample = numpy.array([1,2,3,4,5,6,5,4,3,4,5,7,8,3,2])
        result = self.crop_gradient.local_max_1d(sample)
        assert result.ndim == 2
        assert result.shape[1] == 2
        assert (result == numpy.array([[12, 8], [5, 6]])).all()
        
        # Don't die when given a blank spot
        sample = numpy.ones((3,))
        result = self.crop_gradient.local_max_1d(sample)
        assert result.shape == (0,2)
        
        # Give sorted results
        sample = numpy.random.uniform(0, 1000, 250)
        result = self.crop_gradient.local_max_1d(sample)
        (numpy.diff(result[:,1]) <= 0).all()

    #
    # Region
    #

    def any_region_test(self, method):
        y_maxima = numpy.array([
            [2, 10],
            [10, 10],
            [4, 3]])
        x_maxima = numpy.array([
            [8, 13],
            [16, 12],
            [4, 3]])
        result = method(y_maxima, x_maxima)
        assert result == Region(Point(2, 8), Point(10, 16))
    
    def test_region_impulse(self):
        self.any_region_test(self.crop_gradient.region_impulse)
    
    def test_region_aspect(self):
        self.any_region_test(self.crop_gradient.region_aspect)

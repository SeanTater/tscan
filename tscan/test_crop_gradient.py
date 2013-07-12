import unittest
import numpy
import cv2
from mock import Mock
from common import ImageMeta
from crop_gradient import CropGradient
from crop import Region, Point
import tscantest

class CropGradientTest(unittest.TestCase):
    def setUp(self):
        self.crop_gradient = CropGradient()

    def test_one(self): 
        meta = tscantest.metas[0]
        self.crop_gradient.run(meta)
        
        # Bug: returned bool output, should still be uint8
        self.assertEqual(meta.data.dtype, numpy.uint8) 

    def test_against_reference(self):
        for meta in tscantest.metas:
            region = CropGradient().estimate(meta)
            self.assertTrue(region.almost(meta.reference_crop))
        

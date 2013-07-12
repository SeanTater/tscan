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

    def test_run_one(self):        
        self.crop_gradient.run(tscantest.metas[0])

    def test_against_reference(self):
        for meta in tscantest.metas:
            region = CropGradient().estimate(meta)
            # Compare the crop corners - not done!
            self.assertTrue(region.almost(meta.reference_crop))
        

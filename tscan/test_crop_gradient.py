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
        self.meta = ImageMeta(tscantest.images.values()[0]['filename'])

    def test_run_one(self):        
        self.crop_gradient.run(self.meta)

    def test_against_reference(self):
        for image_name in tscantest.images:
            image_info = tscantest.images[image_name]
            meta = ImageMeta(image_info['filename'])
            region = CropGradient().estimate(meta)
            reference_region = Region(**tscantest.images[image_name]['region'])
            # Compare the crop corners - not done!
            self.assertTrue(region.almost(reference_region))
        

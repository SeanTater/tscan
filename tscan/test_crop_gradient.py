import unittest
import numpy
import cv2
from mock import Mock
from common import ImageMeta
from crop_gradient import CropGradient
import tscantest

class CropGradientTest(unittest.TestCase):
    def setUp(self):
        self.crop_gradient = CropGradient(None, None)
        self.crop_gradient.meta = Mock()
        self.sample_image_filename = tscantest.image.values()[0]

    def test_run_one(self):        
        self.crop_gradient.meta.load.return_value = cv2.imread(self.sample_image_filename)
        self.crop_gradient.run_one()
        self.assertTrue(self.crop_gradient.meta.load.called)
        self.assertTrue(self.crop_gradient.meta.save.called)

    def test_against_reference(self):
        for image_name in tscantest.images:
            image_meta = ImageMeta(image_name['filename'])
            cg = CropGradient(image_meta).estimate()
            # Compare the crop corners - not done!
       
        

import unittest
import numpy
import cv2
import pkg_resources
from mock import Mock
from crop_gradient import CropGradient

class CropGradientTest(unittest.TestCase):
    def setUp(self):
        self.crop_gradient = CropGradient(None, None)
        self.crop_gradient.meta = Mock()

    def test_run_one(self):        
        self.crop_gradient.meta.load.return_value = cv2.imread(pkg_resources.resource_filename("tscantest", "DSCF6076.JPG"))
        self.crop_gradient.run_one()
        self.assertTrue(self.crop_gradient.meta.load.called)
        self.assertTrue(self.crop_gradient.meta.save.called)

    def test_against_reference(self):
        pass
        

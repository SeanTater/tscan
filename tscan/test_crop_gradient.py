import unittest
import numpy
import cv2
from mock import Mock
from crop_gradient import CropGradient

class CropGradientTest(unittest.TestCase):
    def setUp(self):
        self.crop_gradient = CropGradient(None, None)
        self.crop_gradient.meta = Mock()

    def test_run_one(self):        
        self.crop_gradient.meta.load.return_value = cv2.imread("test/sample01.JPG")
        self.crop_gradient.run_one()
        self.assertTrue(self.crop_gradient.meta.load.called)
        self.assertTrue(self.crop_gradient.meta.save.called)
        result = self.crop_gradient.meta.save.call_args[0][0]
        

import unittest
import numpy
import cv2
from mock import Mock
from crop_gradient import CropGradient

class CropGradientTest(unittest.TestCase):
    def setUp(self):
        self.crop_gradient = CropGradient(None, None)
        self.crop_gradient.meta = meta = Mock()
        meta.load.return_value = cv2.imread("test/DSCF6076.JPG")
        #numpy.ones((4,4,3), dtype=numpy.uint8)

    def test_run_one(self):
        self.crop_gradient.run_one()
        self.assertTrue(self.crop_gradient.meta.load.called)

import unittest
import numpy
from mock import Mock
from common import ImageMeta
from crop_corners import CropCorners
import tscantest

class CropCornersTest(unittest.TestCase):
    def setUp(self):
        self.cropcorners = CropCorners()
        self.meta = ImageMeta(tscantest.images.values()[0]['filename'])

    def test_run_one(self):
        self.cropcorners.run(self.meta)

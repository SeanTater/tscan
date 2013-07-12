import unittest
import numpy
from mock import Mock
from common import ImageMeta
from crop_corners import CropCorners
import tscantest

class CropCornersTest(unittest.TestCase):
    def setUp(self):
        self.cropcorners = CropCorners()

    def test_run_one(self):
        self.cropcorners.run(tscantest.metas[0])

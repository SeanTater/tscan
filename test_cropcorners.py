import unittest
import numpy
from mock import Mock
from cropcorners import CropCorners

class CropCornersTest(unittest.TestCase):
    def setUp(self):
        self.cropcorners = CropCorners(None, None)
        self.cropcorners.meta = meta = Mock()
        meta.load.return_value = numpy.ones((4,4), dtype=numpy.uint8)

    def test_run_one(self):
        self.cropcorners.run_one()
        self.assertTrue(self.cropcorners.meta.load.called)

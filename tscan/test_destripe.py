import unittest
import destripe
import numpy
import mock

class TestDestripe(unittest.TestCase):
    def setUp(self):
        self.destripe = destripe.Destripe()
        self.stripe = numpy.array([
            [255, 254, 110, 253],
            [ 10,  10,  10,  10],
            [254, 253,  30, 253],
            [253, 252,  30, 252]], dtype=numpy.uint8)
        self.stripe = numpy.dstack([self.stripe]*3) # Grey
        
    def test_neighbor_threshold(self):
        x_stripe = numpy.swapaxes(self.stripe, 0, 1)
        assert numpy.array_equal(
            self.destripe.neighbor_threshold(self.stripe),
            numpy.array([0, 3, 0, 0]))
        assert numpy.array_equal(
            self.destripe.neighbor_threshold(x_stripe),
            numpy.array([0, 0, 3, 0]))
        
    def test_noise_threshold(self):
        shape = (7, 100, 3)
        noise = numpy.array([10, 50, 75, 12, 100, 2, 0])
        assert numpy.array_equal(
            self.destripe.noise_threshold(shape, noise),
            numpy.array([False, False, True, False, True, False, False]))
        
    def test_noise_mask(self):
        # Should I be mocking more?
        
        assert numpy.array_equal(
            self.destripe.noise_mask(self.stripe),
            numpy.array([
                [0, 0, 1, 0],
                [1, 1, 1, 1],
                [0, 0, 1, 0],
                [0, 0, 1, 0],
                ]),
            )
        
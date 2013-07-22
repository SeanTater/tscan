import unittest
from crop import Region, Point

class TestRegionPoint(unittest.TestCase):
    def test_point(self):
        assert Point(5, 6) == Point(5, 6)
        assert Point(5, 7) != Point(5, 6)
        assert Point(5, 5).distance(Point(5, 6)) == 1
        
    def test_region(self):
        assert Region(Point(5, 5), Point(10, 10)) == Region(Point(5, 5), Point(10, 10))
        assert Region(Point(5, 5), Point(10, 10)) != Region(Point(5, 7), Point(10, 10))
        assert Region(Point(5, 5), Point(10, 10)).mean_distance(
            Region(Point(8, 9), Point(16, 18))) == 7.5

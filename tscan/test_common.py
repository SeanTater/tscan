import unittest
import mock
from common import ImageMeta, NameListSource

class TestImageMeta(unittest.TestCase):
    def test_create(self):
        meta = ImageMeta('filename')
        assert meta.filename == 'filename'
        with self.assertRaises(TypeError):
            ImageMeta()

    def test_load(self):
        meta = ImageMeta('filename')

        with mock.patch('cv2.imread') as m:
            meta.data
            assert m.mock_calls == [mock.call('filename')]

class TestNameListSource(unittest.TestCase):
    def test_create(self):
        source = NameListSource(['foo', 'bar'])
        assert source.filenames == ['foo', 'bar']
        with self.assertRaises(TypeError):
            NameListSource()
    
    def test_generate(self):
        source = NameListSource(['foo', 'bar'])
        metas = list(source.run())
        assert isinstance(metas[0], ImageMeta)
        assert metas[0].filename == 'foo'
        assert metas[1].filename == 'bar'
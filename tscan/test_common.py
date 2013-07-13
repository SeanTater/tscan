import unittest
import mock
from common import ImageMeta, NameListSource, FileSink

class TestImageMeta(unittest.TestCase):
    def test_create(self):
        meta = ImageMeta('filename')
        assert meta.filename == 'filename'
        with self.assertRaises(TypeError):
            ImageMeta()

    def test_load(self):
        # Accessing data loads the image
        with mock.patch('cv2.imread') as m:
            ImageMeta('filename').data
            assert m.mock_calls == [mock.call('filename')]
        
        # Writing to data doesn't load the image - even afterward
        with mock.patch('cv2.imread') as m:
            meta = ImageMeta('filename')
            meta.data = 'stuff'
            assert meta.data == 'stuff'
            assert not m.called

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

class TestFileSink(unittest.TestCase):
    def test_create(self):
        assert FileSink('foo').output_pattern == 'foo'
        assert FileSink().output_pattern == "%(path_noext)s_out%(ext)s"
    
    def test_put(self):
        meta = ImageMeta('/path/to/foo.jpg')
        meta.data = None
        
        fs_plain = FileSink('foo')
        fs_path = FileSink('%(path)s')
        fs_default = FileSink()
        with mock.patch('cv2.imwrite') as m:
            fs_plain.put(meta)
            fs_path.put(meta)
            fs_default.put(meta)
            assert m.mock_calls == [
                mock.call('foo', None),
                mock.call('/path/to/foo.jpg', None),
                mock.call('/path/to/foo_out.jpg', None)]
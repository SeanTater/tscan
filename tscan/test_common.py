import unittest
import mock
from common import ImageMeta, NameListSource, FileSink, Pipe, Progress

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
    
    def test_run(self):
        meta = ImageMeta('/path/to/foo.jpg')
        meta.data = 'example image data'
        
        fs_plain = FileSink('foo')
        fs_path = FileSink('%(path)s')
        fs_default = FileSink()
        with mock.patch('cv2.imwrite') as m:
            fs_plain.run(meta)
            fs_path.run(meta)
            fs_default.run(meta)
            assert m.mock_calls == [
                mock.call('foo', meta.data),
                mock.call('/path/to/foo.jpg', meta.data),
                mock.call('/path/to/foo_out.jpg', meta.data)]

class TestProgress(unittest.TestCase):
    def test_run(self):
        # Can't really test print, settle for do no harm
        m = mock.Mock()
        m.filename = "soandso"
        assert Progress().run(m) is m

class TestPipe(unittest.TestCase):
    def test_create(self):
        p = Pipe('one', 'two', 'three')
        assert p.source == 'one'
        assert p.parts == ('two', 'three')
    
    def test_run(self):
        source = mock.Mock()
        source.run.return_value = iter(['foo'])
        part = mock.Mock()
        part.run.return_value = 'bar'
        p = Pipe(source, part)
        p.run()
        assert source.run.mock_calls == [mock.call()]
        assert part.run.mock_calls == [mock.call('foo')]
        
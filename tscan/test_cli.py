from unittest import TestCase
from mock import Mock, call
from cli import PluginRegistry, Argument
from argparse import Namespace

class TestArgument(TestCase):
    def test_create(self):
        arg = Argument('--abcd', '--efgh', foo='bar')
        assert arg.flags == ('--abcd', '--efgh')
        assert arg.names == ['abcd', 'efgh']
        assert arg.name == 'abcd'
        assert arg.tags == dict(foo='bar')
    
    def test_add_to_argparse(self):
        arg = Argument('--abcd', '--efgh', foo='bar')
        m = Mock()
        arg.add_to_argparse(m)
        assert m.add_argument.mock_calls == [call('--abcd', '--efgh', foo='bar')]

class TestPluginRegistry(TestCase):
    def test_create(self):
        assert PluginRegistry(enabled=True).enabled
        assert not PluginRegistry(enabled=False).enabled
    
    def test_register(self):
        # First do nothing
        fake_plugin = Mock()
        assert PluginRegistry(enabled=False).register(fake_plugin) is fake_plugin
        
        # Now see if it works
        pr = PluginRegistry(enabled=True)
        fake_plugin._args = [
            Argument('required', tag='value'),
            Argument('--optional', tag='value')]
        wrapper = pr.register(fake_plugin)
        assert wrapper is not fake_plugin
        assert fake_plugin in pr.plugins
        
        
        
        # Documented GIGO: argparse handles missing required arguments
        fake_ap_output = Namespace()
        wrapper(Namespace())
        wrapper(Namespace(required='foo'))
        wrapper(Namespace(required='foo', optional='bar'))
        wrapper(Namespace(required='foo', optional='bar', garbage='baz'))
        
        assert fake_plugin.mock_calls == [
            call(),
            call(required='foo'),
            call(required='foo', optional='bar'),
            call(required='foo', optional='bar')]
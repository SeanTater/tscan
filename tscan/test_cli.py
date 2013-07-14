from unittest import TestCase
from mock import Mock, call
from cli import Plugin, Argument
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

class TestPlugin(TestCase):
    def test_register(self):
        class Example(Plugin):
            pass
        
        assert not Plugin.all_plugins
        Plugin.register(Example)
        assert Plugin.all_plugins == {'foo'}
    
    def test_register(self):
        fake_plugin = Mock()
        assert Plugin.register(fake_plugin) is fake_plugin
        
        fake_plugin._args = [
            Argument('required', tag='value'),
            Argument('--optional', tag='value')]
        Plugin.register(fake_plugin)
        assert fake_plugin in Plugin.all_plugins
        
    def init_from_cli(self):
        # Documented GIGO: argparse handles missing required arguments
        class Example(Plugin):
            __init__ = Mock()
            pass
        fake_plugin = Example()
        fake_ap_output = Namespace()
        
        fake_plugin.init_from_cli(Namespace())
        fake_plugin.init_from_cli(Namespace(required='foo'))
        fake_plugin.init_from_cli(Namespace(required='foo', optional='bar'))
        fake_plugin.init_from_cli(Namespace(required='foo', optional='bar', garbage='baz'))
        
        assert fake_plugin.__init__.mock_calls == [
            call(),
            call(required='foo'),
            call(required='foo', optional='bar'),
            call(required='foo', optional='bar')]
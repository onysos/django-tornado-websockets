import os
import unittest

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testsettings")
django.setup()

from django.core.management import call_command
from django.conf import settings
from tornado_websockets.management.commands.runtornado import ReturnValueForTestMode
from tornado_websockets.tests.test_tornadowrapper import TornadoWrapper_reset

class RunTornadoTest(unittest.TestCase):
    def setUp(self):
        try:
            del settings.TORNADO
        except AttributeError:
            pass

        TornadoWrapper_reset()

    def test_with_no_configuration(self):
        with self.assertRaises(ReturnValueForTestMode) as e:
            call_command('runtornado', test_mode="configuration")

        self.assertEqual(e.exception.value, {})

    def test_port_from_command_line(self):
        with self.assertRaises(ReturnValueForTestMode) as e:
            call_command('runtornado', test_mode='port', port=1234)

        self.assertEqual(e.exception.value, 1234)

    def test_port_from_settings(self):
        settings.TORNADO = {
            'port': 9999
        }

        with self.assertRaises(ReturnValueForTestMode) as e:
            call_command('runtornado', test_mode='port')

        self.assertEqual(e.exception.value, 9999)

    def test_port_from_default(self):
        with self.assertRaises(ReturnValueForTestMode) as e:
            call_command('runtornado', test_mode='port')

        self.assertEqual(e.exception.value, 8000)

    def test_port_cascade(self):
        port_command_line = 1234
        port_settings = 9999
        port_default = 8000

        settings.TORNADO = {
            'port': port_settings
        }

        # Should use command line port
        with self.assertRaises(ReturnValueForTestMode) as e:
            call_command('runtornado', test_mode='port', port=port_command_line)

        self.assertEqual(e.exception.value, port_command_line)

        # Should use settings port
        with self.assertRaises(ReturnValueForTestMode) as e:
            call_command('runtornado', test_mode='port')

        self.assertEqual(e.exception.value, port_settings)

        # Should use default port
        del settings.TORNADO
        with self.assertRaises(ReturnValueForTestMode) as e:
            call_command('runtornado', test_mode='port')

        self.assertEqual(e.exception.value, port_default)

    def test_handlers(self):
        with self.assertRaises(ReturnValueForTestMode) as e:
            call_command('runtornado', test_mode='handlers')

        self.assertEqual(e.exception.value, [])

    def test_handlers_from_configuration(self):
        settings.TORNADO = {
            'handlers': [
                ('.*', 'ActuallyNotAnHandler')
            ]
        }

        with self.assertRaises(ReturnValueForTestMode) as e:
            call_command('runtornado', test_mode='handlers')

        self.assertListEqual(e.exception.value, [
            ('.*', 'ActuallyNotAnHandler')
        ])

    def test_settings(self):
        with self.assertRaises(ReturnValueForTestMode) as e:
            call_command('runtornado', test_mode='settings')

        self.assertEqual(e.exception.value, {})

    def test_settings_from_configuration(self):
        settings.TORNADO = {
            'settings': {
                'debug': True
            }
        }

        with self.assertRaises(ReturnValueForTestMode) as e:
            call_command('runtornado', test_mode='settings')

        self.assertDictEqual(e.exception.value, {
            'debug': True
        })

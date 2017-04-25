from unittest import TestCase
import os
from dcb import *

class TestRegistry(TestCase):

  def test_registry(self):

    self.assertEqual(
      sanitize_registry('foo'),
      'FOO',
      msg='sanitize registry (uc)'
    )

    self.assertEqual(
      sanitize_registry('quay.io'),
      'QUAY_IO',
      msg='sanitize registry (dot)'
    )

    self.assertEqual(
      sanitize_registry('foo-bar'),
      'FOO_BAR',
      msg='sanitize registry (dash)'
    )

    envinfix = 'ABC'
    xyz = 'XYZ'
    hij = 'HIJ'

    self.assertEqual(
      Registry(
	envinfix=None,
	reg=None,
	user=None,
	pwd=None,
	email=None,
	dflt_registry=xyz
      ).registry,
      xyz,
      msg='default registry if unspecified'
    )

    self.assertEqual(
      Registry(
	envinfix=None,
	reg=xyz,
	user=None,
	pwd=None,
	email=None
      ).registry,
      xyz,
      msg='registry if specified'
    )

    os.environ['_'.join(['DCB', envinfix, 'REGISTRY'])] = hij
    self.assertEqual(
      Registry(
	envinfix=envinfix,
	reg=None,
	user=None,
	pwd=None,
	email=None
      ).registry,
      hij,
      msg='registry from environment'
    )
      
    

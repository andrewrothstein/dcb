import unittest
import os
from dcb.registry import sanitize_registry, Registry


class TestRegistry(unittest.TestCase):

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

        env_infix = 'ABC'
        xyz = 'XYZ'
        hij = 'HIJ'

        self.assertEqual(
            Registry(
                env_infix='',
                reg='',
                user='',
                pwd='',
                email='',
                dflt_registry=xyz
            ).registry,
            xyz,
            msg='default registry if unspecified'
        )

        self.assertEqual(
            Registry(
                env_infix='',
                reg=xyz,
                user='',
                pwd='',
                email=''
            ).registry,
            xyz,
            msg='registry if specified'
        )

        os.environ['_'.join(['DCB', env_infix, 'REGISTRY'])] = hij
        self.assertEqual(
            Registry(
                env_infix=env_infix,
                reg='',
                user='',
                pwd='',
                email=''
            ).registry,
            hij,
            msg='registry from environment'
        )


if __name__ == '__main__':
    unittest.main()
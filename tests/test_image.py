from unittest import TestCase
from dcb.registry import Registry
from dcb.image import target_image_builder


class TestImage(TestCase):

    def test_image(self):
        r = 'hub.docker.io'
        g = 'andrewrothstein'
        a = 'ansible-alluxio'
        t = 'alpine_3.3'
        i = target_image_builder(
            Registry(
                env_infix='undef',
                reg=r,
                user='andrewrothstein+robot-abc',
                pwd='secret',
                email='andrew.rothstein@gmail.com'
            ),
            group=g,
            app=a,
            tag=t
        )

        self.assertEqual(i.name(), '{0}/{1}:{2}'.format(g, a, t), msg='Image.name')
        self.assertEqual(i.fq_name(), '{0}/{1}/{2}:{3}'.format(r, g, a, t), msg='Image.fq_name')

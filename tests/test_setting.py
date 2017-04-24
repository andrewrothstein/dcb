from unittest import TestCase
import os
from dcb import *

class TestSetting(TestCase):
  
  def test_setting(self):
    abc = "ABC"
    self.assertEqual(Setting("foo").get(dflt=abc), abc, msg="Settings.get dflt value")

  def test_envsetting(self):
    abc = "ABC"
    ghi = "GHI"
    os.environ[abc] = ghi
    self.assertEqual(EnvSetting(abc).get(), ghi, msg="EnvSetting.get lookup")
    self.assertIsNone(EnvSetting(ghi).get(), msg="EnvSetting.get dftl value")

    os.environ['DCB_TEST_REGISTRY'] = ghi
    self.assertEqual(EnvSetting.create('TEST', 'REGISTRY').get(), ghi, msg="EnvSetting.create")

  def test_from_slug(self):
    o = 'andrewrothstein'
    p = 'ansible-transmission'
    slugvar = 'TRAVIS_REPO_SLUG'

    os.environ[slugvar] = "/".join([o, p])
    self.assertEqual(OwnerFromSlugSetting(slugvar).get(), o, "OwnerFromSlugSetting.get")
    self.assertEqual(ProjectFromSlugSetting(slugvar).get(), p, "ProjectFromSlugSetting.get")
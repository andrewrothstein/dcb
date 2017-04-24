from setting import *

class Image:
  def __init__(
      self,
      registry,
      group_settings,
      app_settings,
      tag
  ):
    self.registry = registry
    self.group = resolveSetting(group_settings)
    if not self.group:
      raise_missingarg(
	"{0} group undefined".format(self.registry.envinfix),
	group_settings
      )
    self.app = resolveSetting(app_settings)
    if not self.app:
      raise_missingarg(
        "{0} app undefined".format(self.registry.envinfix),
        app_settings
      )
    self.tag = "latest" if tag is None else tag

  def name(self):
    return "{0}/{1}:{2}".format(self.group, self.app, self.tag)

  def fq_name(self):
    return "{0}/{1}".format(self.registry.registry, self.name())

def group_setting(envinfix) :
  return [ EnvSetting.create(envinfix, 'GROUP') ]

def app_setting(envinfix) :
  return [ EnvSetting.create(envinfix, 'APP') ]

def target_group_settings():
  l = group_setting('TARGET')
  l += [ EnvSetting('CIRCLE_PROJECT_USERNAME'),
	 EnvSetting('CI_PROJECT_NAMESPACE'),
	 OwnerFromSlugSetting('TRAVIS_REPO_SLUG'),
	 OwnerFromSlugSetting('SEMAPHORE_REPO_SLUG') ]
  return l

def target_app_settings():
  l = app_setting('TARGET')
  l += [ EnvSetting('CIRCLE_PROJECT_REPONAME'),
	 EnvSetting('CI_PROJECT_NAME'),
	 ProjectFromSlugSetting('TRAVIS_REPO_SLUG'),
	 ProjectFromSlugSetting('SEMAPHORE_REPO_SLUG') ]
  return l

def raise_missingarg(msg, settingsList):
    raise Exception("Missing Argument", msg + "; considered " + summarizeSettings(settingsList))

def upstream_image_builder(registry, group, app, tag):
  return Image(
    registry,
    [ LiteralSetting(group) ] + group_setting(registry.envinfix),
    [ LiteralSetting(app) ] + app_setting(registry.envinfix),
    tag
  )

def target_image_builder(registry, group, app, tag):
  return Image(
    registry,
    [ LiteralSetting(group) ] + target_group_settings(),
    [ LiteralSetting(app) ] + target_app_settings(),
    tag
  )


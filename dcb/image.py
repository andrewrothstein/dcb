from utils import resolve_arg_list

class Image:
  def __init__(
      self,
      registry,
      group,
      group_el,
      app,
      app_el,
      tag
  ):
    self.registry = registry
    self._group = None
    self._arg_group = group
    self._arg_group_el = group_el
    self._app = None
    self._arg_app = app
    self._arg_app_el = app_el
    self.tag = "latest" if tag is None else tag

  def group(self) :
    if self._group is None:
      self._group = resolve_arg_list(self._arg_group, self._arg_group_el)
      if self._group is None:
        raise_missingarg(
          "{0} group undefined".format(self.registry.envinfix),
          self._arg_group_el
          )
    return self._group
  
  def app(self) :
    if self._app is None:
      self._app = resolve_arg_list(self._arg_app, self._arg_app_el)
      if self._app is None:
        raise_missingarg(
          "{0} app undefined".format(self.registry.envinfix),
          self._arg_app_el
          )
    return self._app
  
  def name(self):
    return "{0}/{1}:{2}".format(self.group(), self.app(), self.tag)

  def fq_name(self):
    return "{0}/{1}".format(self.registry.registry(), self.name())

def group_envlist(envinfix) :
  return ["DCB_{0}_GROUP".format(envinfix)]

def app_envlist(envinfix) :
  return ["DCB_{0}_APP".format(envinfix)]

def raise_missingarg(msg, envlist):
    raise Exception("Missing Argument", msg + " considered [" + ",".join(envlist) + "] environment variables")

def upstream_image_builder(registry, group, app, tag):
  return Image(
    registry,
    group,
    group_envlist(registry.envinfix),
    app,
    app_envlist(registry.envinfix),
    tag
  )

def target_group_envlist(cisystem):
  l = group_envlist("TARGET")
  if (cisystem == "circleci"):
    l.append("CIRCLE_PROJECT_USERNAME")
  elif (cisystem == "gitlabci"):
    l.append("CI_PROJECT_NAMESPACE")
  return l

def target_app_envlist(cisystem):
  l = app_envlist("TARGET")
  if (cisystem == "circleci"):
    l.append("CIRCLE_PROJECT_REPONAME")
  elif (cisystem == "gitlabci"):
    l.append("CI_PROJECT_NAME")
  return l

def target_image_builder(cisystem, registry, group, app, tag):
  return Image(
    registry,
    group,
    target_group_envlist(cisystem),
    app,
    target_app_envlist(cisystem),
    tag
  )


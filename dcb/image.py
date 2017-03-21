from utils import resolve_arg_list

def group_envlist(envinfix) :
  return ["DCB_{0}_GROUP".format(envinfix)]

def app_envlist(envinfix) :
  return ["DCB_{0}_APP".format(envinfix)]

def upstream_image_builder(registry, group, app, tag):
  return Image(
    registry,
    group,
    group_envlist("UPSTREAM"),
    app,
    app_envlist("UPSTREAM"),
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

class Image:
  def __init__(
      self,
      registry,
      group,
      group_envlist,
      app,
      app_envlist,
      tag
  ):
    self.registry = registry
    self.group = resolve_arg_list(group, group_envlist)
    self.app = resolve_arg_list(app, app_envlist)
    self.tag = "latest" if tag is None else tag

  def name(self):
    return "{0}/{1}:{2}".format(self.group, self.app, self.tag)

  def fq_name(self):
    return "{0}/{1}".format(self.registry.registry, self.name())


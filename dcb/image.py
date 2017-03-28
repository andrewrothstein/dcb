from utils import resolve_arg_list

class Image:
  def __init__(
      self,
      registry,
      group,
      app,
      tag
  ):
    self.registry = registry
    self.group = group
    self.app = app
    self.tag = "latest" if tag is None else tag

  def name(self):
    return "{0}/{1}:{2}".format(self.group, self.app, self.tag)

  def fq_name(self):
    return "{0}/{1}".format(self.registry.registry, self.name())


def group_envlist(envinfix) :
  return ["DCB_{0}_GROUP".format(envinfix)]

def app_envlist(envinfix) :
  return ["DCB_{0}_APP".format(envinfix)]

def raise_missingarg(msg, envlist):
    raise Exception("Missing Argument", msg + " [" + ",".join(envlist) + "]")

def upstream_image_builder(registry, group, app, tag):
  upstream_group_el = group_envlist("UPSTREAM")
  upstream_group = resolve_arg_list(group, upstream_group_el)
  if not upstream_group:
    raise_missingarg("upstream group undefined", upstream_group_el)

  upstream_app_el = app_envlist("UPSTREAM")
  upstream_app = resolve_arg_list(app, upstream_app_el)
  if not upstream_app:
    raise_missingarg("upstream app undefined", upstream_app_el)

  return Image(
    registry,
    upstream_group,
    upstream_app,
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
  target_group_el = target_group_envlist(cisystem)
  target_group = resolve_arg_list(group, target_group_el)
  if not target_group:
    raise_missingarg("target group missing", target_group_el)

  target_app_el = target_app_envlist(cisystem)
  target_app = resolve_arg_list(app, target_app_el)
  if not target_app:
    raise_missingarg("target app missing", target_app_el)

  return Image(
    registry,
    target_group,
    target_app,
    tag
  )


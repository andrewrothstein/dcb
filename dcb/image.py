class Image:
  def __init__(self, group, app, registry=None, tag=None):
    self.registry=registry
    self.group=group
    self.app=app
    self.tag = "latest" if tag is None else tag

  def name(self):
    return "{0}/{1}:{2}".format(self.group, self.app, self.tag)

  def fq_name(self):
    if self.registry is None:
      return self.container()
    else:
      return "{0}/{1}".format(self.registry, self.name())


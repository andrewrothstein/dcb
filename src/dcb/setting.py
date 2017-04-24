import os

class Setting:
  def __init__(self, name):
    self._name = name

  def get(self, dflt=None):
    return dflt

class LiteralSetting(Setting):
  def __init__(self, l):
    Setting.__init__(self, "Literal[{0}]".format(l) if l else "NoneSetting")
    self._l = l

  def get(self, dflt=None):
    return self._l
    
class EnvSetting(Setting):
  @staticmethod
  def create(env, kind, sep='_', prefix="DCB") :
    return EnvSetting(sep.join([prefix, env, kind]))
  
  def __init__(self, envkey):
    Setting.__init__(self, "Env[{0}]".format(envkey))
    self._envkey = envkey

  def get(self, dflt=None):
    return os.environ.get(self._envkey, dflt)
  
class SplitSetting(Setting):
  def __init__(self, envkey, sep='/', idx=0):
    Setting.__init__(self, "SplitSetting[{0},{1},{2}]".format(envkey, sep, idx))
    self._envkey = envkey
    self._sep = sep
    self._idx = idx

  def get(self, dflt=None):
    v = os.environ.get(self._envkey)
    if v is not None:
      s = v.split(self._sep)
      return s[self._idx] if len(s) > self._idx else dflt
    return dflt  

class OwnerFromSlugSetting(Setting):
  def __init__(self, envkey) :
    Setting.__init__(self, "OwnerFromSlug[{0}]".format(envkey))
    self._s = SplitSetting(envkey)

  def get(self, dflt=None):
    return self._s.get(dflt=dflt)

class ProjectFromSlugSetting(Setting):
  def __init__(self, envkey) :
    Setting.__init__(self, "ProjectFromSlug[{0}]".format(envkey))
    self._s = SplitSetting(envkey, idx=1)

  def get(self, dflt=None):
    return self._s.get(dflt=dflt)
  
def resolveSetting(settingsList, dflt=None):
  if settingsList is None:
    return dflt
  else:
    r = settingsList[0].get(dflt=dflt)
    return r if r is not None else resolve(settingsList[1:], dflt=dflt)

import logging
from utils import run_it
from setting import *

def sanitize_registry(r) :
  return r.replace('-', '_').replace('.', '_').upper()

def contextualize_setting(s, ty, envinfix, registry) :
  return [
    LiteralSetting(s),
    EnvSetting.create([envinfix, sanitize_registry(registry), ty]),
    EnvSetting.create([envinfix, ty])
  ]

class Registry:
  def __init__(
      self,
      envinfix,
      reg,
      user,
      pwd,
      email,
      dflt_registry='quay.io'
  ) :
    self.envinfix = envinfix
    self.registry = resolveSetting(
      [ LiteralSetting(reg),
	EnvSetting.create([envinfix, 'REGISTRY']),
	LiteralSetting(dflt_registry)
      ]
    )
    self.user = resolveSetting(contextualize_setting(user, 'USER', envinfix, self.registry))
    self.pwd = resolveSetting(contextualize_setting(pwd, 'PWD', envinfix, self.registry))
    self.email = resolveSetting(contextualize_setting(email, 'EMAIL', envinfix, self.registry))
    self._logged_in = False

  def login(self):
    log = logging.getLogger("dcb.login")
    if self.user is None:
      log.debug(
        "{0}: no user specified. skipping registry login.".format(
          self.envinfix
        )
      )
      return False
    elif self.pwd is None:
      log.debug(
        "{0}: no password specified for {1}. skipping registry login.".format(
          self.envinfix,
          self.user
        )
      )
      return False
    else :
      if not self._logged_in:
        log.info(
          "{0}: logging {1} into {2}...".format(
            self.envinfix,
            self.user,
            self.registry
          )
        )
        cmd = ['docker', 'login', '-u', self.user, '-p', self.pwd]
        if self.email:
          cmd += ['-e', self.email]
        cmd += [self.registry]
        run_it(cmd)
        log.info("logged in")
        self._logged_in = True
      else:
        log.debug(
          "{0}: already logged into {1} as {2}".format(
            self.envinfix,
            self.registry,
            self.user
          )
        )
      return True

    

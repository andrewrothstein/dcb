import logging
from utils import run_it
from setting import *

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
    self.registry = resolveSetting(
      [ LiteralSetting(reg),
	EnvSetting.create(envinfix, 'REGISTRY'),
	LiteralSetting(dflt_registry)
      ]
    )
    self.user = resolveSetting([LiteralSetting(user), EnvSetting.create(envinfix, 'USER')])
    self.pwd = resolveSetting([LiteralSetting(pwd), EnvSetting.create(envinfix, 'PWD')])
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

    

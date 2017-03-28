import logging
from utils import resolve_arg, run_it

class Registry:
  def __init__(self, envinfix, reg, user, pwd, email) :
    self.envinfix = envinfix
    self.registry = resolve_arg(reg, "DCB_{0}_REGISTRY".format(envinfix), "quay.io")
    self.user = resolve_arg(user, "DCB_{0}_USER".format(envinfix), None)
    self.pwd = resolve_arg(pwd, "DCB_{0}_PWD".format(envinfix), None)
    self.email = resolve_arg(email, "DCB_{0}_EMAIL".format(envinfix), None)
    self.logged_in = False

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
      if not self.logged_in:
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
        self.logged_in = True
      else:
        log.debug(
          "{0}: already logged into {1} as {2}".format(
            self.envinfix,
            self.registry,
            self.user
          )
        )
      return True

    

import logging
from subprocess import check_call
from utils import resolve_arg

class Registry:
  def __init__(self, envinfix, reg, user, pwd, email) :
    self.registry = resolve_arg(reg, "DCB_{0}_REGISTRY".format(envinfix), "quay.io")
    self.user = resolve_arg(user, "DCB_{0}_USER".format(envinfix), None)
    self.pwd = resolve_arg(pwd, "DCB_{0}_PWD".format(envinfix), None)
    self.email = resolve_arg(email, "DCB_{0}_EMAIL".format(envinfix), None)
    self.logged_in = False

  def login(self):
    log = logging.getLogger("dcb.login")
    if self.user is None:
      log.debug("no user specified. skipping login.")
      return False
    elif self.pwd is None:
      log.debug("no password specified for {0}. not logging in.".format(self.user))
      return False
    else :
      if not self.logged_in:
        log.info("logging {0} into {1}...".format(self.user, self.registry))
        cmd = ['docker',
               'login',
               '-u', self.user,
               '-p', self.pwd]
        if self.email:
          cmd += ['-e', self.email]
        cmd += [self.registry]
        check_call(cmd)
        log.info("logged in")
        self.logged_in = True
      else:
        log.debug("already logged into {0} as {1}".format(self.registry, self.user))
      return True

    

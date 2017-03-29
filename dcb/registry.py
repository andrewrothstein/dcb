import logging
from utils import resolve_arg, run_it

class Registry:
  def __init__(self, envinfix, reg, user, pwd, email) :
    self.envinfix = envinfix
    self._reg = None
    self._arg_reg = reg
    self._user = None
    self._arg_user = user
    self._pwd = None
    self._arg_pwd = pwd
    self._email = None
    self._arg_email = email
    self.logged_in = False

  def registry(self) :
    if self._reg is None:
      self._reg = resolve_arg(
        self._arg_reg,
        "DCB_{0}_REGISTRY".format(self.envinfix), "quay.io"
      )
    return self._reg

  def user(self) :
    if self._user is None:
      self._user = resolve_arg(
        self._arg_user,
        "DCB_{0}_USER".format(self.envinfix),
        None
        )
    return self._user

  def pwd(self) :
    if self._pwd is None:
      self._pwd = resolve_arg(
        self._arg_pwd,
        "DCB_{0}_PWD".format(self.envinfix),
        None
      )
    return self._pwd

  def email(self):
    if self._email is None:
      self._email = resolve_arg(
        self._arg_email,
        "DCB_{0}_EMAIL".format(self.envinfix),
        None
      )
    return self._email
  
  def login(self):
    log = logging.getLogger("dcb.login")
    if self.user() is None:
      log.debug(
        "{0}: no user specified. skipping registry login.".format(
          self.envinfix
        )
      )
      return False
    elif self.pwd() is None:
      log.debug(
        "{0}: no password specified for {1}. skipping registry login.".format(
          self.envinfix,
          self.user()
        )
      )
      return False
    else :
      if not self.logged_in:
        log.info(
          "{0}: logging {1} into {2}...".format(
            self.envinfix,
            self.user(),
            self.registry()
          )
        )
        cmd = ['docker', 'login', '-u', self.user(), '-p', self.pwd()]
        if self.email():
          cmd += ['-e', self.email()]
        cmd += [self.registry()]
        run_it(cmd)
        log.info("logged in")
        self.logged_in = True
      else:
        log.debug(
          "{0}: already logged into {1} as {2}".format(
            self.envinfix,
            self.registry(),
            self.user()
          )
        )
      return True

    

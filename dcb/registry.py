import logging
from subprocess import check_call

def login(registry, user, pwd, email):
  log = logging.getLogger("dcb.login")
  if pwd is not None:
    log.info("logging {0} into {1}...".format(user, registry))
    check_call(['docker',
                'login',
                '-u', user,
                '-p', pwd,
                '-e', email,
                registry])
  else:
    log.info("no password specified for {0}. not logging in.".format(user))
    

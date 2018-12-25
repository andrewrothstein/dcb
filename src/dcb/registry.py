import logging
from dcb.utils import run_it
from dcb.setting import *
from typing import List


def sanitize_registry(r: str) -> str:
    return r.replace('-', '_').replace('.', '_').upper()


def contextualize_setting(s: str, ty: str, env_infix: str, registry: str) -> List[Setting]:
    return [
        LiteralSetting(s),
        EnvSetting.create([env_infix, sanitize_registry(registry), ty]),
        EnvSetting.create([env_infix, ty])
    ]


class Registry:
    def __init__(
            self,
            env_infix: str,
            reg: str,
            user: str,
            pwd: str,
            email: str,
            dflt_registry: str = 'quay.io'
    ):
        self.env_infix = env_infix
        self.registry = resolve_setting(
            [LiteralSetting(reg),
             EnvSetting.create([env_infix, 'REGISTRY']),
             LiteralSetting(dflt_registry)
             ]
        )
        self.user = resolve_setting(contextualize_setting(user, 'USER', env_infix, self.registry))
        self.pwd = resolve_setting(contextualize_setting(pwd, 'PWD', env_infix, self.registry))
        self.email = resolve_setting(contextualize_setting(email, 'EMAIL', env_infix, self.registry))
        self._logged_in = False

    def login(self) -> bool:
        log = logging.getLogger("dcb.login")
        if self.user is None:
            log.debug(
                "{0}: no user specified. skipping registry login.".format(
                    self.env_infix
                )
            )
            return False
        elif self.pwd is None:
            log.debug(
                "{0}: no password specified for {1}. skipping registry login.".format(
                    self.env_infix,
                    self.user
                )
            )
            return False
        else:
            if not self._logged_in:
                log.info(
                    "{0}: logging {1} into {2}...".format(
                        self.env_infix,
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
                        self.env_infix,
                        self.registry,
                        self.user
                    )
                )
            return True

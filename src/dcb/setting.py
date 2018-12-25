import os
from typing import List, Union


class Setting:
    def __init__(self, name: str):
        self.name = name

    def get(self, dflt=None) -> Union[str, None]:
        return dflt


class LiteralSetting(Setting):
    def __init__(self, l: Union[str, None]):
        Setting.__init__(self, "Literal[{0}]".format(l) if l else "NoneSetting")
        self._l = l

    def get(self, dflt=None) -> Union[str, None]:
        return self._l


class EnvSetting(Setting):
    @staticmethod
    def create(l: List[str], sep: str = '_', prefix="DCB"):
        return EnvSetting(
            sep.join([x for x in [prefix] + l if x is not None])
        )

    def __init__(self, env_key: str):
        Setting.__init__(self, "Env[{0}]".format(env_key))
        self._envkey = env_key

    def get(self, dflt=None):
        return os.environ.get(self._envkey, dflt)


class SplitSetting(Setting):
    def __init__(self, env_key: str, sep: str = '/', idx: int = 0):
        Setting.__init__(self, "SplitSetting[{0},{1},{2}]".format(env_key, sep, idx))
        self._envkey = env_key
        self._sep = sep
        self._idx = idx

    def get(self, dflt=None) -> Union[str, None]:
        v = os.environ.get(self._envkey)
        if v is not None:
            s = v.split(self._sep)
            return s[self._idx] if len(s) > self._idx else dflt
        return dflt


class OwnerFromSlugSetting(Setting):
    def __init__(self, env_key: str):
        Setting.__init__(self, "OwnerFromSlug[{0}]".format(env_key))
        self._s = SplitSetting(env_key)

    def get(self, dflt=None) -> Union[str, None]:
        return self._s.get(dflt=dflt)


class ProjectFromSlugSetting(Setting):
    def __init__(self, env_key: str):
        Setting.__init__(self, "ProjectFromSlug[{0}]".format(env_key))
        self._s = SplitSetting(env_key, idx=1)

    def get(self, dflt=None) -> Union[str, None]:
        return self._s.get(dflt=dflt)


class ParentCwdSetting(Setting):
    def __init__(self):
        Setting.__init__(self, "ParentCwdSetting")

    def get(self, dflt=None) -> Union[str, None]:
        return os.path.basename(os.path.dirname(os.getcwd()))


class CwdSetting(Setting):
    def __init__(self):
        Setting.__init__(self, "CwdSetting")

    def get(self, dflt=None) -> Union[str, None]:
        return os.path.basename(os.getcwd())


def resolve_setting(settings: List[Setting], dflt: Union[str, None] = None) -> Union[str, None]:
    if settings:
        r = settings[0].get(dflt=dflt)
        return r if r else resolve_setting(settings[1:], dflt=dflt)
    else:
        return dflt


def summarize_settings(settings: List[Setting]) -> str:
    return '[{0}]'.format(','.join([s.name for s in settings]))

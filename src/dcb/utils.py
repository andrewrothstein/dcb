import logging
import os
import shutil
import subprocess
from dcb.dcbenvironment import DCBEnvironment
from typing import List
from jinja2 import BaseLoader, Template


# inspired by http://blog.endpoint.com/2015/01/getting-realtime-output-using-python.html
def run_it(cmd: List[str]) -> int:
    log = logging.getLogger("dcb.run_it")
    process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            log.info(output.strip())
    rc = process.poll()
    if rc != 0:
        raise subprocess.CalledProcessError(rc, cmd=cmd)
    return rc


def copy_file(tag: str, file: str) -> None:
    log = logging.getLogger("dcb.copy_file")
    target = os.path.join(tag, file)
    log.debug("copying {0} to {1}...".format(file, target))
    shutil.copyfile(file, target)


def docker_build_dir(tag: str, sub_dirs: bool) -> str:
    return tag if sub_dirs else '.'


def dockerfile(tag: str, sub_dirs: bool) -> str:
    if sub_dirs:
        return os.path.join(docker_build_dir(tag, sub_dirs), 'Dockerfile')
    else:
        return "Dockerfile.{0}".format(tag)


def fmt_build_args(build_env: List[str]) -> List[str]:
    log = logging.getLogger("dcb.fmt_build_args")
    r = []
    set_vars = [e for e in build_env if e in os.environ]
    if set_vars:
        for set_var in set_vars:
            r.extend(['--build-arg', set_var])
    log.debug("build args:{0}".format(' '.join(r)))
    return r


def resolve_templates(snippets: List[str], snippet_loader: BaseLoader) -> List[Template]:
    env = DCBEnvironment(loader=snippet_loader)
    return [env.get_template(snippet) for snippet in snippets]



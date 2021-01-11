import logging
from jinja2 import BaseLoader

from dcb.setting import *
from dcb.registry import Registry
from dcb.utils import docker_build_dir, dockerfile, resolve_templates, copy_file, fmt_build_args, run_it


class Image:
    def __init__(
            self,
            env_infix: str,
            registry: Registry,
            group_settings: List[Setting],
            app_settings: List[Setting],
            tag: str
    ):
        self.registry = registry
        self.group = resolve_setting(group_settings)
        if not self.group:
            raise_missingarg(
                '{0} group undefined'.format(env_infix),
                group_settings
            )

        self.app = resolve_setting(app_settings)
        if not self.app:
            raise_missingarg(
                '{0} app undefined'.format(env_infix),
                app_settings
            )
        self.tag = 'latest' if tag is None else tag

    def name(self):
        return '{0}/{1}:{2}'.format(self.group, self.app, self.tag)

    def fq_name(self):
        return '{0}/{1}'.format(self.registry.registry, self.name())


def group_setting(env_infix: str)-> List[Setting]:
    return [EnvSetting.create([env_infix, 'GROUP'])]


def app_setting(env_infix: str)-> List[Setting]:
    return [EnvSetting.create([env_infix, 'APP'])]


def target_group_settings(env_infix: str) -> List[Setting]:
    return group_setting(env_infix) + [
        EnvSetting('CIRCLE_PROJECT_USERNAME'),
        EnvSetting('CI_PROJECT_NAMESPACE'),
        OwnerFromSlugSetting('TRAVIS_REPO_SLUG'),
        OwnerFromSlugSetting('SEMAPHORE_REPO_SLUG'),
        ParentCwdSetting()
    ]


def target_app_settings(env_infix)-> List[Setting]:
    return app_setting(env_infix) + [
        EnvSetting('CIRCLE_PROJECT_REPONAME'),
        EnvSetting('CI_PROJECT_NAME'),
        ProjectFromSlugSetting('TRAVIS_REPO_SLUG'),
        ProjectFromSlugSetting('SEMAPHORE_REPO_SLUG'),
        CwdSetting()
    ]


def raise_missingarg(msg: str, settings: List[Setting]) -> None:
    raise Exception('Missing Argument', msg + '; considered ' + summarize_settings(settings))


def upstream_image_builder(registry, group: str, app: str, tag: str) -> Image:
    env_infix = 'UPSTREAM'
    return Image(
        env_infix,
        registry,
        [LiteralSetting(group)] + group_setting(env_infix),
        [LiteralSetting(app)] + app_setting(env_infix),
        tag
    )


def target_image_builder(registry, group: str, app: str, tag: str) -> Image:
    env_infix = 'TARGET'
    return Image(
        env_infix,
        registry,
        [LiteralSetting(group)] + target_group_settings(env_infix),
        [LiteralSetting(app)] + target_app_settings(env_infix),
        tag
    )

def write(
        upstream_image: Image,
        sub_dirs: bool,
        copy_files: List[str],
        snippet_loader: BaseLoader,
        snippets: List[str]
):
    '''writes ${OS}/Dockerfile and copies some stuff down...'''
    log = logging.getLogger('dcb.write')
    dbd = docker_build_dir(upstream_image.tag, sub_dirs)
    df = dockerfile(upstream_image.tag, sub_dirs)

    if sub_dirs:
        if not os.path.isdir(dbd):
            os.mkdir(dbd)
        for f in copy_files:
            copy_file(dbd, f)

    templates = resolve_templates(snippets, snippet_loader)
    log.info('processing {0} templates to Dockerfile to {0}...'.format(len(templates), df))
    with open(df, 'w') as f:
        for t in templates:
            f.write(
                t.render({
                    'fq_upstream_image': upstream_image.fq_name()
                })
            )
            f.write('\n')


def describe(image: Image) -> int:
    return run_it(['docker', 'images', image.fq_name()])


def build(target_image: Image, build_envs: List[str], sub_dirs: bool) -> int:
    log = logging.getLogger('dcb.build')
    log.info('building the {0} container...'.format(target_image.name()))
    cmd = ['docker', 'build', '--rm=false', "--progress=plain"]
    cmd += fmt_build_args(build_envs)
    cmd += ['-t', target_image.name()]
    cmd += ['-f', dockerfile(target_image.tag, sub_dirs)]
    cmd += [docker_build_dir(target_image.tag, sub_dirs)]
    rc = run_it(cmd)
    if rc == 0:
        describe(target_image)
    else:
        raise Exception('Error building {0}: {1}'.format(target_image, rc))


def push(target_image: Image) -> int:
    log = logging.getLogger('dcb.push')
    log.info('tagging {0} as {1}...'.format(target_image.name(), target_image.fq_name()))
    rc = run_it(['docker', 'tag', target_image.name(), target_image.fq_name()])
    if rc == 0:
        log.info('pushing {0}...'.format(target_image.fq_name()))
        rc = run_it(['docker', 'push', target_image.fq_name()])
        if rc == 0:
            describe(target_image)
        else:
            raise Exception('Error pushing {0}: {1}'.format(target_image.fq_name(), rc))
    else:
        raise Exception('Error tagging {0} as {1}...'.format(target_image.name(), target_image.fq_name()))


def pull(upstream_image: Image) -> int:
    log = logging.getLogger('dcb.pull')
    upstream_image_fq_name = upstream_image.fq_name()
    log.info('pulling {0}...'.format(upstream_image_fq_name))
    rc = run_it(['docker', 'pull', upstream_image_fq_name])
    if rc == 0:
        describe(upstream_image)
    else:
        raise Exception('Error pulling {0}: {1}'.format(upstream_image_fq_name, rc))

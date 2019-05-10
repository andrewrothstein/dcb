#!/usr/bin/env python
import argparse
from jinja2 import FileSystemLoader, PackageLoader
import logging
from dcb.registry import Registry
from dcb.image import target_image_builder, upstream_image_builder, Image
from dcb.compoundloader import CompoundLoader
from dcb.image import write, build, push, pull


def build_parser():
    parser = argparse.ArgumentParser(
        description='generates a bunch of Docker base containers for use testing Ansible roles',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--snippetsdir',
        nargs='*',
        default=[],
        help='paths to the Dockerfile snippets to consider'
    )

    parser.add_argument(
        '--snippet',
        nargs='*',
        default=['from.j2'],
        help='name of the Dockerfile snippets to concatenate'
    )

    parser.add_argument(
        '--ci',
        default='circleci',
        help='CI system to based environment variable lookups from'
    )

    parser.add_argument(
        '--upstreamregistry',
        help='upstream registry for all pull operations'
    )

    parser.add_argument(
        '--upstreamuser',
        help='upstream user to login with. often a robot account'
    )

    parser.add_argument(
        '--upstreampwd',
        help='password to login the upstream user'
    )

    parser.add_argument(
        '--upstreamemail',
        help='email address to use when logging into the upstream registry'
    )

    parser.add_argument(
        '--upstreamgroup',
        help='upstream image group'
    )

    parser.add_argument(
        '--upstreamapp',
        help='upstream container name'
    )

    parser.add_argument(
        '--targetregistry',
        help='target registry for all push operations'
    )

    parser.add_argument(
        '--targetgroup',
        help='target image group'
    )

    parser.add_argument(
        '--targetuser',
        help='target user to login with. often a robot account'
    )

    parser.add_argument(
        '--targetpwd',
        help='password to login the target user'
    )

    parser.add_argument(
        '--targetemail',
        help='email address to use when logging into the target registry'
    )

    parser.add_argument(
        '--targetapp',
        help='target container name'
    )

    parser.add_argument(
        '--write',
        help='write the subdirs for the specified tag'
    )

    parser.add_argument(
        '--pull',
        help='pull upstream image for specified tags'
    )

    parser.add_argument(
        '--build',
        help='build the Docker container for the specified tag'
    )

    parser.add_argument(
        '--push',
        help='push built Docker container to the target registry for specified tag'
    )

    parser.add_argument(
        '--writeall',
        action='store_true',
        help='write the subdirs for all tags'
    )

    parser.add_argument(
        '--subdirs',
        action='store_true',
        help='assume Dockerfiles, etc. are in tag/platform based subdirectories'
    )

    parser.add_argument(
        '--copyfile',
        nargs='*',
        default=[],
        help='list of files to copy into subdir when using --write and --subdirs'
    )

    parser.add_argument(
        '--pullall',
        action='store_true',
        help='pull upstream images for all tags'
    )

    parser.add_argument(
        '--buildall',
        action='store_true',
        help='build Docker containers for all tags'
    )

    parser.add_argument(
        '--pushall',
        action='store_true',
        help='push built Docker containers to the specified target registry for all tags'
    )

    parser.add_argument(
        '--buildenv',
        nargs='*',
        default=['HTTP_PROXY', 'HTTPS_PROXY', 'FTP_PROXY', 'NO_PROXY',
                 'http_proxy', 'https_proxy', 'ftp_proxy', 'no_proxy'],
        help='list of environment variables to pass through as build args if defined'
    )

    parser.add_argument(
        '--alltags',
        nargs='*',
        default=[
            "ubuntu_trusty",
            "ubuntu_xenial",
            "ubuntu_bionic",
            "fedora_23",
            "fedora_24",
            "fedora_25",
            "fedora_26",
            "fedora_27",
            "fedora_28",
            "fedora_29",
            "fedora_30",
            "centos_7",
            "alpine_3.3",
            "alpine_3.4",
            "alpine_3.5",
            "alpine_3.6",
            "alpine_3.7",
            "alpine_3.8",
            "alpine_3.9",
            "alpine_edge",
            "archlinux_latest",
            "debian_jessie",
            "debian_stretch",
        ],
        help='set of all platforms for the --{write,pull,build}all options'
    )

    return parser


def run():
    log = logging.getLogger("dcb.run")
    args = build_parser().parse_args()

    upstream_registry = Registry(
        "UPSTREAM",
        args.upstreamregistry,
        args.upstreamuser,
        args.upstreampwd,
        args.upstreamemail
    )

    target_registry = Registry(
        "TARGET",
        args.targetregistry,
        args.targetuser,
        args.targetpwd,
        args.targetemail
    )

    def upstream_image(t: str) -> Image:
        return upstream_image_builder(
            upstream_registry,
            args.upstreamgroup,
            args.upstreamapp,
            t
        )

    def target_image(t: str) -> Image:
        return target_image_builder(
            target_registry,
            args.targetgroup,
            args.targetapp,
            t
        )

    snippets_loader = CompoundLoader(
        [PackageLoader(__name__, 'snippets')]
        + [FileSystemLoader(sd) for sd in args.snippetsdir]
    )

    # for --buildall --build foo yield: [x, ..., foo]
    def which_tags(inclevery, every, mine):
        x = every if inclevery else []
        if mine:
            x += [mine]
        return x

    def any_tags(inclevery, every, mine):
        return mine or (inclevery and every)

    for tag in which_tags(args.writeall, args.alltags, args.write):
        write(
            upstream_image(tag),
            args.subdirs,
            args.copyfile,
            snippets_loader,
            args.snippet
        )

    if any_tags(args.pullall, args.alltags, args.pull) or any_tags(args.buildall, args.alltags, args.build):
        upstream_registry.login()

    for tag in which_tags(args.pullall, args.alltags, args.pull):
        pull(upstream_image(tag))

    for tag in which_tags(args.buildall, args.alltags, args.build):
        build(target_image(tag), args.buildenv, args.subdirs)

    if any_tags(args.pushall, args.alltags, args.push):
        if not target_registry.login():
            log.warning("not logged into target registry! skipping push!")
        else:
            for tag in which_tags(args.pushall, args.alltags, args.push):
                push(target_image(tag))


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    run()

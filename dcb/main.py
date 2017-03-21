#!/usr/bin/env python

import logging
import argparse
from dcb import *
from jinja2 import Environment, FileSystemLoader, PackageLoader

def build_parser() :

  parser = argparse.ArgumentParser(
    description='generates a bunch of Docker base containers for use testing Ansible roles',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )

  parser.add_argument(
    '--snippetsdir',
    help='path to the Dockerfile snippets'
  )

  parser.add_argument(
    '--snippet',
    default='Dockerfile.onbuild',
    help='file name of the Dockerfile snippet'
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
    help='upstream image group',
    required=True
  )

  parser.add_argument(
    '--upstreamapp',
    help='upstream container name',
    required=True
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
    '--writesubdirs',
    action='store_true'
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

  return parser

def main() :

  args = build_parser().parse_args()

  upstreamregistry = Registry(
    "UPSTREAM",
    args.upstreamregistry,
    args.upstreamuser,
    args.upstreampwd,
    args.upstreamemail
  )

  targetregistry = Registry(
    "TARGET",
    args.targetregistry,
    args.targetuser,
    args.targetpwd,
    args.targetemail
  )
  
  def upstream_image(tag):
    return upstream_image_builder(
      upstreamregistry,
      args.upstreamgroup,
      args.upstreamapp,
      tag
    )

  def target_image(tag):
    return target_image_builder(
      args.ci,
      targetregistry,
      args.targetgroup,
      args.targetapp,
      tag
    )
  
  all_tags = [
    "ubuntu_trusty",
    "ubuntu_xenial",
    "fedora_23",
    "fedora_24",
    "fedora_25",
    "centos_7",
    "alpine_3.3",
    "alpine_3.4",
    "alpine_3.5",
    "alpine_edge",
    "debian_jessie",
  ]

  snippetsloader = FileSystemLoader(args.snippetsdir) if args.snippetsdir else PackageLoader(__name__, 'snippets')
     
  if (args.writeall) :
    map(lambda tag : write(upstream_image(tag), args.writesubdirs, snippetsloader, args.snippet), all_tags)

  if (args.write):
    write(upstream_image(args.write), args.writesubdirs, snippetsloader, args.snippet)

  if (args.pullall or args.pull or args.buildall or args.build):
    upstreamregistry.login()
    
  if (args.pullall) :
    map(lambda tag : pull(upstream_image(tag)), all_tags)

  if (args.pull):
    pull(upstream_image(args.pull))
    
  if (args.buildall) :
    map(lambda tag: build(target_image(tag), args.buildenv, args.writesubdirs), all_tags)

  if (args.build):
    build(target_image(args.build), args.buildenv, args.writesubdirs)

  if (args.pushall or args.push):
    if not targetregistry.login():
      log.warn("not logged into target registry! skipping push!")
    else:
      if (args.pushall) :
        map(lambda tag: push(target_image(tag)), all_tags)

      if (args.push) :
        push(target_image(args.push))

if __name__ == '__main__' :
    logging.basicConfig(
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
      level=logging.DEBUG
    )

    log = logging.getLogger("dcb.__main__")
    log.info("welcome to the dcb...")
    main()
    log.info("exiting the dcb!")


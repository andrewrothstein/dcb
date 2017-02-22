#!/usr/bin/env python

import logging
import argparse
from jinja2 import Environment, FileSystemLoader, PackageLoader

def main() :

  parser = argparse.ArgumentParser(
    description='generates a bunch of Docker base containers for use testing Ansible roles'
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
    '--upstreamregistry',
    default='quay.io',
    help='upstream registry for all pull operations'
  )
  
  parser.add_argument(
    '--upstreamgroup',
    default='andrewrothstein'
  )

  parser.add_argument(
    '--upstreamuser',
    default='andrewrothstein'
  )

  parser.add_argument(
    '--upstreampwd',
    help='password to login the upstream user'
  )

  parser.add_argument(
    '--upstreamemail',
    default='andrew.rothstein@gmail.com'
  )

  parser.add_argument(
    '--upstreamapp',
    default='docker-ansible'
  )

  parser.add_argument(
    '--targetregistry',
    default='quay.io',
    help='target registry for all push operations'
  )
  
  parser.add_argument(
    '--targetgroup',
    default='andrewrothstein'
  )

  parser.add_argument(
    '--targetuser',
    default='andrewrothstein'
  )
  
  parser.add_argument(
    '--targetpwd',
    help='password to login the target user'
  )

  parser.add_argument(
    '--targetemail',
    default='andrew.rothstein@gmail.com'
  )

  parser.add_argument(
    '--targetapp',
    default='docker-ansible-role'
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
    help='list of environment variables to pass through as build args'
  )
  
  args = parser.parse_args()

  login(
    args.upstreamregistry,
    args.upstreamuser,
    args.upstreampwd,
    args.upstreamemail
  )

  login(
    args.targetregistry,
    args.targetuser,
    args.targetpwd,
    args.targetemail
  )
  
  def upstream_image(tag):
    return Image(
      group=args.upstreamgroup,
      app=args.upstreamapp,
      registry=args.upstreamregistry,
      tag=tag
      )

  def target_image(tag):
    return Image(
      group=args.targetgroup,
      app=args.targetapp,
      registry=args.targetregistry,
      tag=tag
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

  if (args.pullall) :
    map(lambda tag : pull(upstream_image(tag)), all_tags)

  if (args.pull):
    pull(upstream_image(args.pull))
    
  snippetsloader = FileSystemLoader(args.snippetsdir) if args.snippetsdir else PackageLoader(__name__, 'snippets')
     
  if (args.writeall) :
    map(lambda tag : write(upstream_image(tag), args.writesubdirs, snippetsloader, args.snippet), all_tags)

  if (args.write):
    write(upstream_image(args.write), args.writesubdirs, snippetsloader, args.snippet)

  if (args.buildall) :
    map(lambda tag: build(target_image(tag), args.buildenv, args.writesubdirs), all_tags)

  if (args.build):
    build(target_image(args.build), args.buildenv, args.writesubdirs)
    
  if (args.pushall) :
    map(lambda tag: push(target_image(tag)), all_tags)

  if (args.push) :
    push(target_image(args.push))

if __name__ == '__main__' :
    logging.basicConfig(
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
      level=logging.INFO
    )

    log = logging.getLogger("dcb.__main__")
    log.info("welcome to the dcb...")
    main()
    log.info("exiting the dcb!")


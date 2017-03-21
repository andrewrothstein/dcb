import logging
import os
import shutil
from jinja2 import Environment, FileSystemLoader
from string import join
from subprocess import check_call

def resolve_arg(arg, envname, dflt = None) :
  return os.environ.get(envname, dflt) if arg is None else arg

# descend through a list of environment variables in search of a hit...
def resolve_arg_list(arg, envnames, dflt = None):
  if arg is not None:
    return arg
  elif not envnames:
    return dflt
  else :
    return os.environ.get(envnames[0], resolve_arg_list(arg, envnames[1:], dflt))

def copy_file(tag, file) :
  shutil.copyfile(file, '{0}/{1}'.format(tag, file))

def dockerbuilddir(tag, writesubdirs):
  return tag if writesubdirs else '.'

def dockerfile(tag, writesubdirs):
  if writesubdirs:
    return "{0}/Dockerfile".format(dockerbuilddir(tag, writesubdirs))
  else:
    return "Dockerfile.{0}".format(tag)

def fmt_build_args(buildenv):
  log = logging.getLogger("dcb.fmt_build_args")
  setvars = filter(lambda e: e in os.environ, buildenv)
  r = reduce(list.__add__, map(lambda e: ["--build-arg", e], setvars))
  log.info("build args:{0}".format(r))
  return r
      
def describe(image):
  check_call(['docker', 'image', 'ls', image.fq_name()])

# writes ${OS}/Dockerfile and copies some stuff down...
def write(upstream_image, writesubdirs, snippetloader, snippet):
  log = logging.getLogger("dcb.write")
  dbd = dockerbuilddir(upstream_image.tag, writesubdirs)
  df = dockerfile(upstream_image.tag, writesubdirs)

  if (writesubdirs):
    if (not os.path.isdir(dbd)) :
      os.mkdir(dbd)
    copy_file(dbd, "requirements.yml")
    copy_file(dbd, "playbook.yml")
    
  template = Environment(loader=snippetloader).get_template(snippet)
  log.info("writing Dockerfile to {0}...".format(df))
  with open(df, 'w') as f:
    f.write(template.render({ "fq_upstream_image" : upstream_image.fq_name()}))

def build(target_image, buildenvs, writesubdirs):
  log = logging.getLogger("dcb.build")
  log.info("building the {0} container...".format(target_image.name()))
  cmd = ['docker', 'build', '--rm=false']
  cmd += fmt_build_args(buildenvs)
  cmd += ['-t', target_image.name()]
  cmd += ['-f', dockerfile(target_image.tag, writesubdirs)]
  cmd += [dockerbuilddir(target_image.tag, writesubdirs)]
  r = check_call(cmd, shell=False)
  describe(target_image)
  return r

def push(target_image):
  log = logging.getLogger("dcb.push")
  log.info("tagging {0} as {1}...".format(target_image.name(), target_image.fq_name()))
  check_call(['docker', 'tag', target_image.name(), target_image.fq_name()])
  log.info("pushing {0}...".format(target_image.fq_name()))
  r = check_call(['docker',
                  'push',
                  target_image.fq_name()],
                 shell=False)
  describe(target_image)
  return r

def pull(upstream_image) :
  log = logging.getLogger("dcb.pull")
  log.info("pulling {0}...".format(upstream_image.fq_name()))
  r = check_call(['docker',
                  'pull',
                  upstream_image.fq_name()],
                 shell=False)
  describe(upstream_image)
  return r


import logging
import os
import shutil
import subprocess
from dcbenvironment import DCBEnvironment
from compoundloader import CompoundLoader
from jinja2 import FileSystemLoader
from string import join

# inspired by http://blog.endpoint.com/2015/01/getting-realtime-output-using-python.html
def run_it(cmd):
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

def copy_file(tag, file) :
  log = logging.getLogger("dcb.copy_file")
  target = '{0}/{1}'.format(tag, file)
  log.debug("copying {0} to {1}...".format(file, target))
  shutil.copyfile(file, target)

def dockerbuilddir(tag, subdirs):
  return tag if subdirs else '.'

def dockerfile(tag, subdirs):
  if subdirs:
    return "{0}/Dockerfile".format(dockerbuilddir(tag, subdirs))
  else:
    return "Dockerfile.{0}".format(tag)

def fmt_build_args(buildenv):
  log = logging.getLogger("dcb.fmt_build_args")
  setvars = filter(lambda e: e in os.environ, buildenv)
  r = reduce(list.__add__, map(lambda e: ["--build-arg", e], setvars)) if setvars else []
  log.debug("build args:{0}".format(r))
  return r
      
def describe(image):
  return run_it(['docker', 'images', image.fq_name()])

def resolve_templates(snippets, snippetloader):
  def resolve(snippets, env):
    if len(snippets) == 0:
      return []
    else:
      return [env.get_template(snippets[0])] + resolve(snippets[1:], env)
  return resolve(snippets, DCBEnvironment(loader=snippetloader))

# writes ${OS}/Dockerfile and copies some stuff down...
def write(upstream_image, subdirs, copyfiles, snippetloader, snippets):
  log = logging.getLogger("dcb.write")
  dbd = dockerbuilddir(upstream_image.tag, subdirs)
  df = dockerfile(upstream_image.tag, subdirs)

  if (subdirs):
    if (not os.path.isdir(dbd)) :
      os.mkdir(dbd)
    for f in copyfiles:
      copy_file(dbd, f)
    
  templates = resolve_templates(snippets, snippetloader)
  log.info("processing {0} templates to Dockerfile to {0}...".format(len(templates), df))
  with open(df, 'w') as f:
    for t in templates:
      f.write(
	t.render({
	  "fq_upstream_image" : upstream_image.fq_name()
	})
      )
      f.write("\n")

def build(target_image, buildenvs, subdirs):
  log = logging.getLogger("dcb.build")
  log.info("building the {0} container...".format(target_image.name()))
  cmd = ['docker', 'build', '--rm=false']
  cmd += fmt_build_args(buildenvs)
  cmd += ['-t', target_image.name()]
  cmd += ['-f', dockerfile(target_image.tag, subdirs)]
  cmd += [dockerbuilddir(target_image.tag, subdirs)]
  rc = run_it(cmd)
  describe(target_image)
  return rc


def push(target_image):
  log = logging.getLogger("dcb.push")
  log.info("tagging {0} as {1}...".format(target_image.name(), target_image.fq_name()))
  run_it(['docker', 'tag', target_image.name(), target_image.fq_name()])
  log.info("pushing {0}...".format(target_image.fq_name()))
  r = run_it(['docker', 'push', target_image.fq_name()])
  describe(target_image)
  return r

def pull(upstream_image) :
  log = logging.getLogger("dcb.pull")
  log.info("pulling {0}...".format(upstream_image.fq_name()))
  r = run_it(['docker', 'pull', upstream_image.fq_name()])
  describe(upstream_image)
  return r


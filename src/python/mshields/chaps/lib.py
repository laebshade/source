"""Chaps library."""
#  pylint: disable=E0401

from __future__ import absolute_import, print_function

import os

from sarge import capture_stdout, run


def git_toplevel():
  """
  Grab absolute path of repo using git command.

  :returns: git.stdout.text.rstrip()
  :rtype: str.
  """
  git = capture_stdout("git rev-parse --show-toplevel")
  return git.stdout.text.rstrip()


def rel_cwd():
  """
  Given the cwd and git_toplevel result, constructs the relative path difference.

  :returns: os.path.relpath
  :rtype: str.
  """
  return os.path.relpath(os.getcwd(), git_toplevel())


def targets(path, args):
  """
  Assembles Fully Qualified Pants Targets (FQPT).

  :returns: space-delimited FQPT targets.
  :rtype: str.
  """
  return " ".join(["{0}{1}".format(path, target) for target in args])


def pants(args):
  """
  Grab the top level dir from git command, chdir and execute ./pants with given args.

  :param args: arguments to pass to sarge.
  :type args: str
  :returns: _pants
  :rtype: sarge `obj`
  """
  os.chdir(git_toplevel())
  _pants = run("./pants %s" % args)

  return _pants


def pants_list(args):
  """
  Non-interactive output of pants list parsed to only show bare targets without paths.

  :param args: arguments to pass to sarge.
  :type args: str
  :returns: _pants
  """
  os.chdir(git_toplevel())
  _pants_list = capture_stdout("./pants %s" % args)

  for target in _pants_list.stdout.text.split("\n"):
    if ":" in target:
      bare_target = target.split(":", 1)[-1]
      print(":%s" % bare_target)


def pytest_options(options):
  """Generate pytest_options flags."""
  flags = []

  if options.verbose:
    verbosity = int(options.verbose)
    flags.append("%s" % "".join(["v" for _ in range(verbosity)]))
  elif options.failfast:
    flags.append("xvv")

  if flags:
    return "-%s" % "".join(flags)

  return ""


def app_usage(commands_and_docstrings):
  """
  Create an app usage string.

  :param commands_and_docstrings: commands and docstrings from __doc__.
  :param type: dict
  :returns: _app_usage
  :rtype: str
  """
  "\n".join([
    "    %-22%s" % (command, 

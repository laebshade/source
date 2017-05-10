"""
Chaps, a relative dir pants wrapper for Python targets.

Chaps makes it easier to interact with your Pants Build System without having
to type out lengthy path names.

Let's say you're in your project dir and want to build a binary. So you:

  $ cd ~/workspace/source ; ./pants binary path/to/target:target

That's just a pain.  This is where chaps comes in:

  $ chaps binary :target

How about just running your code?  We have you covered:

  $ chaps run :target -- args

Interested in dropping into an iPython REPL?  You're golden:

  $ chaps repl :target

Working in your tests directory and want to run tests?   Chaps has a shortcut for
that, too:

  $ chaps test :target

If you're looking to resolve formatting issues, look no more for the fmt goal;:

  $ chaps fmt :target

Note: chaps only works with targets in your current work directory (cwd).  Fall
back to calling pants directly if you need something else.
"""
# pylint: disable=E0401,E0611,E1101

from __future__ import absolute_import, print_function

import os

from sarge import capture_stdout, run
from twitter.common import app, log

log.LogOptions().disable_disk_logging()


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


@app.command(name="binary")
def binary_goal(args):
  """
  Create a binary using pants.

  :param args: relative targets.
  :param type: list `str`.
  """
  _targets = targets(rel_cwd(), args)
  log.debug("chaps targets: %s", _targets)

  pants_args = "binary {0}".format(_targets)
  pants(pants_args)


@app.command(name="fmt")
def fmt_goal(args):
  """
  Fix common format issues using pants fmt goal.

  :param args: relative targets.
  :param type: list `str`.
  """
  _targets = targets(rel_cwd(), args)
  log.debug("chaps targets: %s", _targets)

  pants_args = "fmt {0}".format(_targets)
  pants(pants_args)


@app.command(name="list")
def list_goal():
  """List relative path pants targets."""
  path = rel_cwd()
  pants_args = "list {0}:".format(path)

  pants_list(pants_args)


@app.command(name="repl")
def repl_goal(args):
  """
  Enter an ipython REPL.

  :param args: relative targets.
  :type args: list `str`.
  """
  _targets = targets(rel_cwd(), args)
  log.debug("chaps targets: %s", _targets)

  pants_args = "repl --repl-py-ipython {0}".format(_targets)
  pants(pants_args)


@app.command(name="run")
def run_goal(args):
  """
  Run a target using pants.

  :param args: relative targets.
  :param type: list `str`.
  """
  single_target = args[0]
  _targets = targets(rel_cwd(), [single_target])
  run_args = " ".join(args[1:])

  log.debug("chaps targets: %s", _targets)

  pants_args = "run {0} {1}".format(_targets, run_args)
  pants(pants_args)


@app.command_option(
  "--all", action="store_true", dest="all", default=False,
  help="Test all targets in path name simliar to cwd.",
)
@app.command_option(
  "--coverage", action="store_true", dest="coverage", default=False, help="Python test coverage.",
)
@app.command_option(
  "--failfast", action="store_true", default=False, help="Python stop on first error.",
)
@app.command_option(
  "--verbose", action="store", default=0, help="Python test verbosity.",
)
@app.command(name="test")
def test_goal(args, options):
  """
  Use test.pytest goal with pants.

  :param args: relative targets.
  :param type: list `str`.
  :param options: twitter.common.app options.
  :param type: obj
  """
  if options.all:
    _targets = "%s::" % rel_cwd().replace('src', 'tests')
  else:
    _targets = targets(rel_cwd(), args)

  log.debug("chaps targets: %s", _targets)

  def options_flags():
    """Generate pytest_options flags."""
    flags = []

    if options.verbose:
      verbosity = int(options.verbose)
      flags.append("%s" % "".join(["v" for _ in range(verbosity)]))
    elif options.failfast:
      flags.append("xvv")

    if flags:
      return "-%s" % "".join(flags)
    else:
      return ""


  pants_args = "test.pytest  {0} {1} {2}".format(
    "--coverage=%d" % int(options.coverage),
    "--test-pytest-options='%s'" % options_flags(), _targets
  )
  pants(pants_args)


app.add_option("--quiet", "-q", default=False)
app.set_usage("chaps [goal]")
app.main()

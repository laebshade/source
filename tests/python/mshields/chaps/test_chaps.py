"""Chaps tests."""
# pylint: disable=E0401


def test_git_toplevel(mocker):
  """Test git_toplevel function."""
  git_toplevel = mocker.Mock()

  git_toplevel.return_value = "/home/repos/source"
  assert git_toplevel() == "/home/repos/source"


def test_targets():
  """Test targets function."""
  from mshields.chaps.chaps import targets

  path = "test/to/path"
  args = [":one_target", ":second_target"]

  assert targets(path, args) == "test/to/path:one_target test/to/path:second_target"

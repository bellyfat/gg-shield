import subprocess
from typing import Any, List

import click


COMMAND_TIMEOUT = 45
GIT_PATH = "git"


def is_git_dir() -> bool:
    try:
        check_git_dir()
        return True
    except click.ClickException:
        return False


def check_git_dir() -> None:
    """ Check if folder is git directory. """
    check_git_installed()
    with subprocess.Popen(
        [GIT_PATH, "status"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ) as process:
        if process.wait():
            raise click.ClickException("Not a git directory.")


def get_git_root() -> str:
    return shell(["git", "rev-parse", "--show-toplevel"])


def check_git_installed() -> None:
    """ Check if git is installed. """
    with subprocess.Popen(
        [GIT_PATH, "--help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ) as process:
        if process.wait():
            raise click.ClickException("Git is not installed.")


def shell(command: List[str], timeout: int = COMMAND_TIMEOUT) -> str:
    """ Execute a command in a subprocess. """
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return result.stdout.decode("utf-8").rstrip()
    except subprocess.CalledProcessError:
        pass
    except subprocess.TimeoutExpired:
        raise click.Abort('Command "{}" timed out'.format(" ".join(command)))
    except Exception as exc:
        raise click.ClickException(f"Unhandled exception: {str(exc)}")

    return ""


def shell_split(command: List[str], **kwargs: Any) -> List[str]:
    return shell(command, **kwargs).split("\n")


def get_list_commit_SHA(commit_range: str) -> List[str]:
    """
    Retrieve the list of commit SHA from a range.
    :param commit_range: A range of commits (ORIGIN...HEAD)
    """

    commit_list = shell_split(
        [GIT_PATH, "rev-list", "--reverse", *commit_range.split()]
    )
    if "" in commit_list:
        commit_list.remove("")
        # only happens when git rev-list doesn't error
        # but returns an empty range, example git rev-list HEAD...

    return commit_list

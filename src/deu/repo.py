from os import mkdir
from os.path import join, exists
import click

from typing import TextIO, Any, Callable


class Repo:
    def __init__(self, repo_path: str):
        self.path = repo_path


def read_module(repo: Repo, module_name: str, on_read_file: Callable[[TextIO], Any]):
    repo_path = join(repo.path, module_name)
    json_path = join(repo_path, f"{module_name}.json")
    if not exists(repo_path):
        raise FileNotFoundError(f"{json_path} not found.")
    else:
        with open(json_path, "r") as f:
            return on_read_file(f.read())


def write_module(repo: Repo, module_name: str, on_write_file: Callable[[TextIO], None]):
    repo_path = join(repo.path, module_name)
    json_path = join(repo_path, f"{module_name}.json")
    if not exists(repo_path):
        mkdir(repo_path)

    with open(json_path, "w") as f:
        on_write_file(f)


pass_repo = click.make_pass_decorator(Repo)

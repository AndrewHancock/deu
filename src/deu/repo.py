import click


class Repo:
    def __init__(self, repo_path: str):
        self.path = repo_path


pass_repo = click.make_pass_decorator(Repo)

import click
from keyring import set_password, get_password
from getpass import getpass
from os.path import join, exists
from os import mkdir

from pydantic import BaseModel

from deu.repo import Repo
from deu.repo import pass_repo


class CredEntry(BaseModel):
    key: str
    user_name: str


class CredRepo(BaseModel):
    cred_entries: list[CredEntry]


_cred_repo = None
_cred_repo_by_key = {}


@click.group()
@pass_repo
def cred(repo: Repo):
    pass


@cred.command()
@click.option('--key', required=True)
@click.option('--user-name', required=True)
@click.password_option()
@pass_repo
@click.pass_context
def add(ctx, repo, key, user_name, password):
    if _get_cred_entry(repo, key):
        ctx.fail(f"Entry already exists for {key}")
    else:
        print("Password 'set'. (debug mode. password not actually set.")
        # set_password(service_name, user_name, password)

        entry = CredEntry(key=key, user_name=user_name)
        _set_cred_entry(repo, entry)


@cred.command()
@click.option('--key', required=True)
@click.option('--user-name', required=True)
@click.password_option()
@pass_repo
@click.pass_context
def update(ctx, repo, key, user_name, password):
    if not _get_cred_entry(repo, key):
        ctx.fail(f'Could not find entry for key {key}')
    else:
        # set password
        entry = CredEntry(key=key, user_name=user_name)
        _set_cred_entry(repo, entry)


@cred.command()
@pass_repo
def list(repo):
    read_cred_repo(repo)
    print("Credential entries:")
    for e in _cred_repo.cred_entries:
        print(f"\tKey: {e.key}\tUser Name: {e.user_name}")


def read_cred_repo(repo: Repo) -> CredRepo:
    global _cred_repo
    global _cred_repo_by_key
    if not _cred_repo:
        repo_path = join(repo.path, "cred")
        json_path = join(repo_path, "cred.json")
        if not exists(repo_path):
            _cred_repo = CredRepo(cred_entries=[])
        else:
            _cred_repo = CredRepo.parse_file(json_path)
            _cred_repo_by_key = {v.key: v for v in _cred_repo.cred_entries}
    return _cred_repo


def write_cred_repo(path: str, cred_repo: CredRepo):
    repo_path = join(path, "cred")
    json_path = join(repo_path, "cred.json")
    if not exists(repo_path):
        mkdir(repo_path)

    with open(json_path, "w") as f:
        f.write(cred_repo.json())


def _get_cred_entry(repo: Repo, cred_key: str):
    global _cred_repo
    global _cred_repo_by_key

    if not _cred_repo:
        read_cred_repo(repo)

    if cred_key in _cred_repo_by_key:
        return _cred_repo_by_key[cred_key]
    else:
        return None


def _set_cred_entry(repo: Repo, entry: CredEntry):
    if entry.key in _cred_repo_by_key:
        i = 0
        for i, e in enumerate(_cred_repo.cred_entries):
            if e.key == entry.key:
                break
        _cred_repo.cred_entries[i] = entry
    else:
        _cred_repo.cred_entries.append(entry)
    _cred_repo_by_key[entry.key] = entry
    write_cred_repo(repo.path, _cred_repo)



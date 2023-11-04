import click

from keyring import set_password, get_password

from pydantic import BaseModel

from deu.repo import Repo, pass_repo, read_module, write_module
from typing import List


class CredEntry(BaseModel):
    key: str
    user_name: str


class CredRepo(BaseModel):
    cred_entries: List[CredEntry]


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
    try:
        # Ensure entry does NOT exist
        get_cred_entry(repo, key)
        ctx.fail(f"Entry already exists for {key}")
    except KeyError as e:
        set_password(key, user_name, password)
        print("Password saved. ")

        entry = CredEntry(key=key, user_name=user_name)
        _set_cred_entry(repo, entry)


@cred.command()
@click.option('--key', required=True)
@click.option('--user-name', required=True)
@click.password_option()
@pass_repo
@click.pass_context
def update(ctx, repo, key, user_name, password):
    try:
        # Ensure the entry exists
        get_cred_entry(repo, key)
        # set password
        set_password(key, user_name, password)
        print("Password updated.")

        entry = CredEntry(key=key, user_name=user_name)
        _set_cred_entry(repo, entry)
    except KeyError as e:
        ctx.fail(f"Cred entry not found for {key}.")


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
        try:
            _cred_repo = read_module(repo, 'cred', lambda f: CredRepo.model_validate_json(f))
            _cred_repo_by_key = {v.key: v for v in _cred_repo.cred_entries}
        except FileNotFoundError as e:
            _cred_repo = CredRepo(cred_entries=[])

    return _cred_repo


def write_cred_repo(repo: Repo, cred_repo: CredRepo):
    write_module(repo, 'cred', lambda f: f.write(cred_repo.model_dump_json()))


def get_cred_entry(repo: Repo, cred_key: str):
    global _cred_repo
    global _cred_repo_by_key

    if not _cred_repo:
        read_cred_repo(repo)

    return _cred_repo_by_key[cred_key]


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
    write_cred_repo(repo, _cred_repo)



from enum import Enum
from typing import List

import click
from pydantic import BaseModel

from deu.repo import read_module, Repo, write_module, pass_repo

ConnType = Enum('Type', ['sql-server'])


class ConnEntry(BaseModel):
    key: str
    cred_key: str
    host: str


class ConnRepo(BaseModel):
    entries: List[ConnEntry]


_conn_repo: list[ConnEntry] = None
_conn_repo_entries_by_key: dict[str, ConnEntry] = None

@click.group()
@pass_repo
def conn(repo: Repo):
    pass


@conn.command()
@click.option('--key', required=True)
@click.option('--cred_key', required=True)
@click.option('--host', required=True)
@pass_repo
@click.pass_context
def add(ctx, repo, key: str, cred_key: str, host: str):
    try:
        # Ensure entry does NOT exist
        get_conn_entry(repo, key)
        ctx.fail(f"Entry already exists for {key}")
    except KeyError:
        entry = ConnEntry(key=key, cred_key=cred_key, host=host)
        _set_conn_entry(repo, entry)


@conn.command()
@click.option('--key', required=True)
@click.option('--cred_key', required=True)
@click.option('--host', required=True)
@pass_repo
@click.pass_context
def update(ctx, repo,  key: str, cred_key: str, host: str):
    try:
        # Ensure the entry exists
        get_conn_entry(repo, key)
        # set password
        entry = ConnEntry(key=key, cred_key=cred_key, host=host)
        _set_conn_entry(repo, entry)
    except KeyError:
        ctx.fail(f"Conn entry not found for {key}.")


def read_conn_repo(repo: Repo) -> ConnRepo:
    global _conn_repo
    global _conn_repo_entries_by_key

    if not _conn_repo:
        try:
            _conn_repo = read_module(repo, 'conn', lambda f: ConnRepo.model_validate_json(f))
            _conn_repo_entries_by_key = {v.key: v for v in _conn_repo.entries}
        except FileNotFoundError:
            _conn_repo = ConnRepo(entries=[])
            _conn_repo_entries_by_key = {}

    return _conn_repo


def write_conn_repo(repo: Repo, cred_repo: ConnRepo):
    write_module(repo, 'conn', lambda f: f.write(cred_repo.model_dump_json()))


def get_conn_entry(repo: Repo, conn_key: str):
    global _conn_repo
    global _conn_repo_entries_by_key

    if not _conn_repo:
        read_conn_repo(repo)

    return _conn_repo_entries_by_key[conn_key]


def _set_conn_entry(repo: Repo, entry: ConnEntry):
    global _conn_repo_entries_by_key

    if entry.key in _conn_repo_entries_by_key:
        i = 0
        for i, e in enumerate(_conn_repo.entries):
            if e.key == entry.key:
                break
        _conn_repo.entries[i] = entry
    else:
        _conn_repo.entries.append(entry)
    _conn_repo_entries_by_key[entry.key] = entry
    write_conn_repo(repo, _conn_repo)

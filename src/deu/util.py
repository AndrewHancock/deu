import os
import sys
from os.path import exists, join
import click

from deu.cred import cred
from deu.conn import conn
from deu.repo import Repo
from deu.db import db


@click.group()
@click.pass_context
def deu(ctx):
    cwd = os.getcwd()
    repo_dir = join(cwd, '.deu')
    if not exists(repo_dir) and not ctx.invoked_subcommand == 'init':
        print("Repo does not exist. Run `init` sub-command to create one first.")
        ctx.abort()
    else:
        ctx.obj = Repo(repo_dir)


@deu.command()
def init():
    cwd = os.getcwd()
    repo_dir = join(cwd, '.deu')
    if exists(repo_dir):
        print(".deu directory already exists.")
    else:
        os.mkdir(repo_dir)
        print(".deu directory created.")


@deu.command()
def test():
    print("Hello!")


deu.add_command(cred)
deu.add_command(conn)
deu.add_command(db)


if __name__ == '__main__':
    deu(sys.argv[1:])

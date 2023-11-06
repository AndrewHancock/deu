import click
import pyodbc
from deu.repo import pass_repo, Repo
from deu.cred import get_cred_entry, get_password
from deu.conn import get_conn_entry
from sqlalchemy import create_engine, MetaData, Table, inspect


@click.group()
@pass_repo
def db(repo: Repo) -> None:
    pass


@db.command()
@click.option('--cred_key', required=True)
@pass_repo
def test(repo: Repo, cred_key: str) -> None:

    conn_entry = get_conn_entry(repo, cred_key)
    cred_entry = get_cred_entry(repo, conn_entry.cred_key)
    password = get_password(cred_entry.key, cred_entry.user_name)

    engine = create_engine(f"mssql+pyodbc://{cred_entry.user_name}:{password}@{conn_entry.host}/AdventureWorksLT2019?driver=SQL+Server", use_setinputsizes=False)
    print("Inspecting database...")
    insp = inspect(engine)

    for table in insp.get_table_names():
        print(f"\nTable {table}:")
        for c in insp.get_columns(table_name=table):
            print(f"\t{c['name']}: {c['type']}")

def _conn_str(host, username, password, database) -> str:
    return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={database};UID={username};PWD={password}'

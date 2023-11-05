import click
import pyodbc
from deu.repo import pass_repo, Repo
from deu.cred import get_cred_entry, get_password
from deu.conn import get_conn_entry


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

    conn = pyodbc.connect(_conn_str(conn_entry.host, cred_entry.user_name, password, 'AdventureWorksLT2019'))
    sql_qry = """
                SELECT 
                    TOP 5 c.CustomerID, 
                    c.CompanyName, 
                    COUNT(soh.SalesOrderID) AS OrderCount 
                FROM 
                    SalesLT.Customer AS c 
                LEFT OUTER JOIN SalesLT.SalesOrderHeader AS soh ON c.CustomerID = soh.CustomerID 
                GROUP BY 
                    c.CustomerID, 
                    c.CompanyName 
                ORDER BY 
                    OrderCount DESC;
               """

    cursor = conn.cursor()
    cursor.execute(sql_qry)

    records = cursor.fetchall()
    for r in records:
        print(f"{r.CustomerID}\t{r.OrderCount}\t{r.CompanyName}")


def _conn_str(host, username, password, database) -> str:
    return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={database};UID={username};PWD={password}'

import pandas as pd
from app_config import dbname, host, port, user, password, conn_str
import psycopg2
from sqlalchemy import create_engine
from retry import retry

# with open("app_pgkey.txt", "r") as file:
#     conn_str = file.read()

con = create_engine(conn_str)
conn = psycopg2.connect(
    database=dbname, user=user, password=password, host=host, port=port
)


def check_table_exist(name):
    sqls = f"""
    SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{name}'
    """
    if pd.read_sql(sqls, con=con).shape[0] > 0:
        return True
    else:
        return False


@retry(tries=3, delay=2)
def execute_sql(sql_statement):
    cursor = conn.cursor()
    cursor.execute(sql_statement)
    conn.commit()
    cursor.close()


def write_new_df_to_pg(
    df, name, primary_key=[], single_indexes=[], if_exists="replace"
):
    # Create new table and write to PGSQL
    if df.index.name is not None:
        df = df.reset_index()
    df.columns = df.columns.str.lower()
    df.to_sql(name=name, con=con, index=False, if_exists=if_exists)

    # Create Primary Key and Indexes
    commands = []
    if len(primary_key) > 0:
        key_args = ",".join(primary_key)
        s0 = f"""ALTER TABLE {name} ADD PRIMARY KEY ({key_args});"""
        commands.append(s0)

    if len(single_indexes) > 0:
        for idx in single_indexes:
            s1 = f"""CREATE INDEX {name}_idx_{idx} ON {name}({idx});"""
            commands.append(s1)
    if len(commands) > 0:
        for cmd in commands:
            execute_sql(cmd)


def write_append_df_to_pg(df, name, if_exists="append"):
    if df.index.name is not None:
        df = df.reset_index()
    df.columns = df.columns.str.lower()
    df.to_sql(name=name, con=con, index=False, if_exists=if_exists)

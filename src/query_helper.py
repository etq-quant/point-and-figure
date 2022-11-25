import pandas as pd
from pg import con


def get_ids(table="prices_kl", column="id"):
    ids = pd.read_sql(f"SELECT DISTINCT({column}) FROM {table};", con=con)[
        column
    ].tolist()
    ids.remove("B05L892")
    ids = ["B05L892"] + ids
    return ids


def get_dates(table="prices_kl", column="date", to_str=False):
    dts = pd.read_sql(f"SELECT DISTINCT({column}) FROM {table};", con=con)[
        column
    ].tolist()
    if to_str:
        dts = [dt.strftime("%Y-%m-%d") for dt in dts]
    return dts


def get_max_dt(table):
    try:
        max_dt = pd.read_sql(f"SELECT MAX(date) FROM {table};", con=con)[
            "max"
        ].tolist()[0]
        return max_dt
    except Exception:
        return None


def get_id_name_mapper(table="gics_kl"):
    df = pd.read_sql(f"SELECT id, common_name FROM {table};", con=con)
    return df.set_index("id")["common_name"].to_dict()


def query_latest_table(table):
    max_dt = get_max_dt(table)
    if max_dt is None:
        raise Exception(f"Table not found: {table}")
    df = pd.read_sql(f"SELECT * FROM {table} WHERE date='{max_dt}';", con=con)
    return df


def query_id(_id, tables=[], limit=10000):
    sqls = []
    sqls1 = f"""
        SELECT * FROM (
            SELECT *
            FROM prices_kl
            WHERE id='{_id}'
            ORDER BY date DESC
            LIMIT {limit}
        ) a
        ORDER BY date ASC;
    """
    sqls.append(sqls1)
    for table in tables:
        sqls2 = f"""
            SELECT * FROM (
                SELECT *
                FROM {table}
                WHERE id='{_id}'
                ORDER BY date DESC
                LIMIT {limit}
            ) a
            ORDER BY date ASC;
        """
        sqls.append(sqls2)
    cols = []
    dfs = []
    for sql_statement in sqls:
        df = pd.read_sql(sql_statement, con=con)
        df = df.drop(columns=["id"])
        df = df.set_index("date")
        df_cols=df.columns.tolist()
        sub_cols=[j for j in df_cols if j not in cols]
        cols+=sub_cols
        dfs.append(df[sub_cols])

    fdf = pd.concat(dfs, axis=1)
    return fdf

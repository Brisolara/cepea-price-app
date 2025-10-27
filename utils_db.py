import os
import sqlalchemy as sa

def get_engine():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Missing DATABASE_URL environment variable.")
    return sa.create_engine(url, pool_pre_ping=True)

def ensure_schema():
    eng = get_engine()
    with eng.begin() as conn:
        sql = (open("db/schema.sql", "r", encoding="utf-8").read())
        # naive split by ';' to execute sequentially
        buf = ""
        for line in sql.splitlines(True):
            buf += line
            if line.strip().endswith(";"):
                conn.exec_driver_sql(buf)
                buf = ""

def upsert_commodities(defaults):
    eng = get_engine()
    with eng.begin() as conn:
        for slug, name in defaults:
            conn.exec_driver_sql(
                "insert into commodity(slug,name) values(%s,%s) on conflict(slug) do nothing",
                (slug, name))

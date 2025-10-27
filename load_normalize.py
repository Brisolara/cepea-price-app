import pandas as pd
import sqlalchemy as sa
from pathlib import Path
from unidecode import unidecode
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Missing DATABASE_URL")

ENGINE = sa.create_engine(DATABASE_URL)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [unidecode(str(c)).strip().lower() for c in df.columns]
    rename_map = {}
    if "data" in df.columns: rename_map["data"] = "ref_date"
    if "valor r$" in df.columns: rename_map["valor r$"] = "price_brl"
    if "valor rs" in df.columns: rename_map["valor rs"] = "price_brl"
    if "valor us$" in df.columns: rename_map["valor us$"] = "price_usd"
    if "especificacao" in df.columns: rename_map["especificacao"] = "spec"
    df = df.rename(columns=rename_map)
    if "ref_date" not in df.columns or "price_brl" not in df.columns:
        raise ValueError("Não encontrei colunas esperadas no Excel do CEPEA.")
    df["ref_date"] = pd.to_datetime(df["ref_date"], dayfirst=True).dt.date
    if "spec" not in df.columns: df["spec"] = None
    if "price_usd" not in df.columns: df["price_usd"] = None
    return df[["ref_date","spec","price_brl","price_usd"]]

def commodity_id_map(conn):
    cid = pd.read_sql("select id, slug from commodity", conn)
    return dict(zip(cid["slug"], cid["id"]))

def load_folder(folder: Path, conn):
    cid_map = commodity_id_map(conn)
    for xlsx in folder.glob("*.xlsx"):
        slug = xlsx.stem.split("_")[0].lower().replace(" ", "-")
        if slug not in cid_map:
            print("slug não cadastrado, pulando:", slug)
            continue
        df = pd.read_excel(xlsx)
        df = normalize_columns(df)
        df["commodity_id"] = cid_map[slug]
        df["source_url"] = "https://www.cepea.org.br/br/consultas-ao-banco-de-dados-do-site.aspx"
        df[["commodity_id","ref_date","spec","price_brl","price_usd","source_url"]]            .to_sql("price_daily", conn, if_exists="append", index=False, method="multi", chunksize=500)
        print("carregado:", slug, len(df), "linhas")

def refresh_matview(conn):
    conn.exec_driver_sql("refresh materialized view price_variations;")

def main():
    eng = ENGINE
    with eng.begin() as conn:
        base = Path("data/raw")
        if not base.exists():
            print("Sem diretório data/raw para processar.")
            return
        for day in sorted(base.iterdir()):
            if day.is_dir():
                print("Processando:", day)
                load_folder(day, conn)
        refresh_matview(conn)

if __name__ == "__main__":
    main()

import pandas as pd
import streamlit as st

from utils_db import get_engine, ensure_schema, upsert_commodities

DEFAULT_COMMODITIES = [
    ("boi-gordo", "Boi gordo"),
    ("bezerro", "Bezerro"),
    ("soja", "Soja"),
    ("milho", "Milho"),
    ("cafe", "Café"),
    ("acucar", "Açúcar"),
    ("etanol", "Etanol"),
    ("trigo", "Trigo"),
    ("frango", "Frango"),
    ("suino", "Suíno"),
    ("arroz", "Arroz"),
    ("mandioca", "Mandioca"),
    ("leite", "Leite"),
    ("ovos", "Ovos"),
    ("tilapia", "Tilápia"),
    ("dolar", "Dólar"),
]

st.set_page_config(page_title="Agro Preços CEPEA", layout="wide")

@st.cache_resource
def _engine():
    ensure_schema()
    upsert_commodities(DEFAULT_COMMODITIES)
    return get_engine()

ENG = _engine()

@st.cache_data(ttl=600)
def list_commodities():
    return pd.read_sql("select slug, name from commodity order by name", ENG)

@st.cache_data(ttl=600)
def load_variations(slug: str):
    q = """
    select c.name, p.*
    from price_variations p
    join commodity c on c.id = p.commodity_id
    where c.slug = %(slug)s
    order by ref_date desc
    """
    return pd.read_sql(q, ENG, params={"slug": slug})

st.sidebar.title("Filtros")
commodities = list_commodities()
if commodities.empty:
    st.warning("Sem commodities cadastradas ainda.")
    st.stop()

slug = st.sidebar.selectbox(
    "Commodity",
    commodities["slug"].tolist(),
    index=0,
    format_func=lambda s: commodities.set_index("slug").loc[s, "name"],
)

window = st.sidebar.selectbox("Janela", ["30","180","360"], index=0)

df = load_variations(slug)
if df.empty:
    st.title("Agro Preços CEPEA — CEPEA/ESALQ (CC BY-NC)")
    st.info("Ainda não há dados carregados. Aguarde a primeira execução do ETL (18h30 BRT) ou rode manualmente.")
    st.stop()

name = df["name"].iloc[0]
st.title(f"{name} — CEPEA/ESALQ (CC BY-NC)")

last = df.iloc[0]
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Preço (R$)", f"{last['price_brl']:.2f}")
col2.metric("D/D-1", f"{((last['var_d1'] or 0)*100):.2f}%")
col3.metric("30d", f"{((last['var_30d'] or 0)*100):.2f}%")
col4.metric("180d", f"{((last['var_180d'] or 0)*100):.2f}%")
col5.metric("360d", f"{((last['var_360d'] or 0)*100):.2f}%")

def plot_window(days: int):
    cut = df.sort_values("ref_date").tail(days)
    st.line_chart(cut.set_index("ref_date")["price_brl"], height=260, use_container_width=True)

st.subheader(f"Últimos {window} dias")
plot_window(int(window))

with st.expander("Créditos e Fonte"):
    st.caption("Fonte: CEPEA/ESALQ/USP — dados sob licença CC BY-NC 4.0. Atualização diária após 18h (horário de Brasília).")

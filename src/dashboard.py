"""Dashboard BI de exemplo - Streamlit.

Rodar (com o venv ativado):
    streamlit run src/dashboard.py

Troque o CSV em CAMINHO_DADOS pelos seus dados quando tiver.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

CAMINHO_DADOS = Path(__file__).resolve().parent.parent / "data" / "exemplo_vendas.csv"

st.set_page_config(page_title="Dashboard BI", page_icon="📊", layout="wide")


@st.cache_data
def carregar_dados(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(caminho, parse_dates=["data"])
    df["mes"] = df["data"].dt.to_period("M").astype(str)
    return df


df = carregar_dados(CAMINHO_DADOS)

st.title("📊 Dashboard de Vendas (exemplo)")
st.caption("Kit BI inicial — troque pelos seus dados em data/ quando quiser.")

# ---- Filtros na barra lateral ----
st.sidebar.header("Filtros")
regioes = st.sidebar.multiselect(
    "Região", sorted(df["regiao"].unique()), default=sorted(df["regiao"].unique())
)
categorias = st.sidebar.multiselect(
    "Categoria", sorted(df["categoria"].unique()), default=sorted(df["categoria"].unique())
)

filtro = df[df["regiao"].isin(regioes) & df["categoria"].isin(categorias)]

# ---- KPIs (numeros principais) ----
col1, col2, col3 = st.columns(3)
col1.metric("Faturamento total", f"R$ {filtro['total'].sum():,.0f}")
col2.metric("Itens vendidos", f"{int(filtro['quantidade'].sum()):,}")
col3.metric("Ticket médio", f"R$ {filtro['total'].mean():,.0f}")

st.divider()

# ---- Graficos ----
c1, c2 = st.columns(2)

with c1:
    st.subheader("Faturamento por mês")
    por_mes = filtro.groupby("mes", as_index=False)["total"].sum()
    fig = px.line(por_mes, x="mes", y="total", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Faturamento por categoria")
    por_cat = filtro.groupby("categoria", as_index=False)["total"].sum()
    fig = px.bar(por_cat, x="categoria", y="total", color="categoria")
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Top produtos")
    por_prod = (
        filtro.groupby("produto", as_index=False)["total"].sum()
        .sort_values("total", ascending=False)
    )
    fig = px.bar(por_prod, x="total", y="produto", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Participação por região")
    por_reg = filtro.groupby("regiao", as_index=False)["total"].sum()
    fig = px.pie(por_reg, names="regiao", values="total", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Dados detalhados")
st.dataframe(filtro, use_container_width=True)

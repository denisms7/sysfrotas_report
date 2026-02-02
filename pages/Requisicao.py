import streamlit as st
import pandas as pd
import plotly.express as px
from data.data import data

# -------------------------------------------------
# Configuração da página
# -------------------------------------------------
st.set_page_config(
    page_title="Combustível utilizado (Litros)",
    page_icon="⛽",
    layout="wide",
)

st.title("⛽ Combustível utilizado (Litros)")

# -------------------------------------------------
# Carregamento dos dados
# -------------------------------------------------
st.cache_data.clear()
df_bruto = data()



# -------------------------------------------------
# Filtros laterais
# -------------------------------------------------
st.sidebar.subheader("🎯 Filtros", divider=True)

ano_min = int(df_bruto["ano"].min())
ano_max = int(df_bruto["ano"].max())

ano_inicio, ano_fim = st.sidebar.slider(
    "Selecione o intervalo de anos",
    min_value=ano_min,
    max_value=ano_max,
    value=(ano_min, ano_max),
    step=1,
)

df = df_bruto.loc[
    (df_bruto["ano"] >= ano_inicio) &
    (df_bruto["ano"] <= ano_fim)
].copy()




req_min = int(df_bruto["quantidade"].min())
req_max = int(df_bruto["quantidade"].max())


req_inicio, req_fim = st.slider(
    "Selecione os Litros",
    min_value=req_min,
    max_value=req_max,
    value=(600, req_max),
    step=10,
)

df_req = df.loc[(df["quantidade"] >= req_inicio) & (df["quantidade"] <= req_fim)]


st.markdown(
    f"**Requisições no período:** {len(df_req)}",
    unsafe_allow_html=True,
)



df_req = df_req[["codigo_abastecimento", "data_hora", "codigo_veiculo", "nome_veiculo", "placa", "combustivel_tipo", "quantidade", "valor_total"]]

colunas_exibicao = {
    "codigo_abastecimento": "Código Requisição",
    "data_hora": "Data/Hora",
    "codigo_veiculo": "ID Veículo",
    "nome_veiculo": "Veículo",
    "placa": "Placa",
    "combustivel_tipo": "Tipo Combustível",
    "quantidade": "Quantidade (L)",
    "valor_total": "Valor Total (R$)",
}

df_req_exibicao = (
    df_req[
        [
            "codigo_abastecimento",
            "data_hora",
            "codigo_veiculo",
            "nome_veiculo",
            "placa",
            "combustivel_tipo",
            "quantidade",
            "valor_total",
        ]
    ]
    .rename(columns=colunas_exibicao)
)

st.dataframe(
    df_req_exibicao,
    use_container_width=True,
)


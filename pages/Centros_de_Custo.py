import streamlit as st
from data.data import load_data_centros


# -------------------------------------------------
# Configuração da página
# -------------------------------------------------
st.set_page_config(
    page_title="Centro de custo",
    page_icon="⛽",
    layout="wide",
)

st.title("⛽ Centro de custo")


# -------------------------------------------------
# Carregamento dos dados
# -------------------------------------------------
with st.spinner("Carregando dados..."):
    df = load_data_centros()


df_secretaria = df.rename(
    columns={
        "centro_de_custos": "Centro de Custo",
        "secretaria": "Secretaria",
    }
)

st.dataframe(
    df_secretaria,
    width='stretch',
)

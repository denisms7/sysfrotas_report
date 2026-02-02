import streamlit as st
from data.data import centros


df_secretaria = centros()


# -------------------------------------------------
# Configuração da página
# -------------------------------------------------
st.set_page_config(
    page_title="Centro de custo",
    page_icon="⛽",
    layout="wide",
)

st.title("⛽ Centro de custo")

df_secretaria = df_secretaria.rename(
    columns={
        "centro_de_custos": "Centro de Custo",
        "secretaria": "Secretaria",
    }
)

st.dataframe(
    df_secretaria,
    use_container_width=True,
)

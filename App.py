import streamlit as st
import pandas as pd
import plotly.express as px
from data.data import data

df = data()

# -------------------------------------------------
# Configuração da página
# -------------------------------------------------
st.set_page_config(
    page_title="Combustível",
    page_icon="⛽",
    layout="wide"
)

st.title("⛽ Combustível utilizado")
st.subheader("Fonte de dados SysFrotas")


# -------------------------------------------------
# Valor gasto Reais e Litros
# -------------------------------------------------
opcao = st.segmented_control(
    "Visualização",
    options=["💵 Valor Total", "⛽ Quantidade"],
    default="💵 Valor Total",
)


if opcao == "💵 Valor Total":
    total_anual = (
        df
        .groupby(['combustivel_tipo', 'ano_mes'], as_index=False)
        .agg(valor=('valor_total', 'sum'))
    )
    eixo_y = 'valor'
    titulo_y = 'Valor Total (R$)'
else:
    total_anual = (
        df
        .groupby(['combustivel_tipo', 'ano_mes'], as_index=False)
        .agg(valor=('quantidade', 'sum'))
    )
    eixo_y = 'valor'
    titulo_y = 'Litros abastecidos'


fig = px.line(
    total_anual,
    x='ano_mes',
    y=eixo_y,
    color='combustivel_tipo',
    markers=True,
    title='Evolução Mensal por Combustível'
)

fig.update_layout(
    xaxis_title='Ano-Mês',
    yaxis_title=titulo_y,
    legend_title_text='Combustível',
)

st.plotly_chart(fig, width="stretch")


# -------------------------------------------------
# Valor por Litro
# -------------------------------------------------
fig_litro = px.line(
    df,
    x='data_hora',
    y='valor_unitario',
    color='combustivel_tipo',
    markers=True,
    title='Valor do combustivel por unidade'
)

fig_litro.update_layout(
    xaxis_title='Data Hora',
    yaxis_title='Valor por Litro'
)

st.plotly_chart(fig_litro, width="stretch")


# -------------------------------------------------
# Valor por Litro
# -------------------------------------------------

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


# -------------------------------------------------
# Filtrar período
# -------------------------------------------------
st.sidebar.subheader("🎯 Filtros", divider=True)

ano_min = int(df["ano"].min())
ano_max = int(df["ano"].max())

ano_inicio, ano_fim = st.sidebar.slider(
    "Selecione o intervalo de anos",
    min_value=ano_min,
    max_value=ano_max,
    value=(ano_min, 2025),
    step=1,
)

df = df.loc[
    (df["ano"] >= ano_inicio) & (df["ano"] <= ano_fim)
]

st.subheader(f"Fonte de dados SysFrotas: {ano_min} a {ano_max}")


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
# Valor / Quantidade por Secretaria
# -------------------------------------------------
total_anual_secretaria = (
    df
    .groupby(['ano_mes', 'secretaria'], as_index=False)
    .agg(valor=('valor_total', 'sum'))
)

fig_secretaria = px.line(
    total_anual_secretaria,
    x='ano_mes',
    y=eixo_y,
    color='secretaria',
    markers=True,
    title='Evolução Mensal por Secretaria (Valor Total)'
)

fig_secretaria.update_layout(
    xaxis_title='Ano-Mês',
    yaxis_title=titulo_y,
    legend_title_text='Secretaria',
)


fig_secretaria_pizza = px.line(
    total_anual_secretaria,
    x='ano_mes',
    y=eixo_y,
    color='secretaria',
    markers=True,
    title='Evolução Mensal por Secretaria (Valor Total)'
)

fig_secretaria_pizza.update_layout(
    xaxis_title='Ano-Mês',
    yaxis_title=titulo_y,
    legend_title_text='Secretaria',
)


st.plotly_chart(fig_secretaria, width="stretch")

# -------------------------------------------------
# Total Geral por Secretaria (Gráfico Agrupado)
# -------------------------------------------------
total_por_secretaria = (
    df
    .groupby('secretaria', as_index=False)
    .agg(valor=('valor_total', 'sum'))
)

# Ordena pelo valor total (do maior para o menor)
total_por_secretaria = total_por_secretaria.sort_values(
    by='valor',
    ascending=False
)

fig_secretaria_pizza = px.bar(
    total_por_secretaria,
    x='secretaria',
    y=eixo_y,
    text_auto='.2s',
    title='Total Geral por Secretaria',
    subtitle=f"Periodo: {ano_min} - {ano_max}",
)

fig_secretaria_pizza.update_layout(
    xaxis_title='Secretaria',
    yaxis_title=titulo_y,
)

st.plotly_chart(fig_secretaria_pizza, use_container_width=True)




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



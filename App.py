import streamlit as st
import pandas as pd
import plotly.express as px
from data.data import data

st.cache_data.clear()

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
].copy()  # Adicione .copy() aqui

st.subheader(f"Fonte de dados SysFrotas: {ano_min} a {ano_max}")


opcao_coluna = st.sidebar.segmented_control(
    "Tipo de Visualização",
    options=["Mensal", "Anual"],
    default="Mensal",
)

if opcao_coluna == "Anual":
    coluna_geral = "ano"
    coluna_geral_nome = "Ano"
else:
    coluna_geral = "ano_mes"
    coluna_geral_nome = "Ano-Mês"



opcao_diesel = st.sidebar.segmented_control(
    "Agrupar Diesel S-10 e S-500",
    options=["Separar", "Agrupar"],
    default="Separar",
)

opcao_gasolina = st.sidebar.segmented_control(
    "Agrupar Gasolina e Gasolina Aditivada",
    options=["Separar", "Agrupar"],
    default="Separar",
)


st.sidebar.info("O Agrupamentos soma o valor total e litros dos tipos selecionados.")

if opcao_diesel == "Agrupar":
    df["combustivel_tipo"] = df["combustivel_tipo"].replace(
        {
            "DIESEL S-10": "DIESEL AGRUPADO",
            "DIESEL S-500": "DIESEL AGRUPADO",
        }
    )

if opcao_gasolina == "Agrupar":
    df["combustivel_tipo"] = df["combustivel_tipo"].replace(
        {
            "GASOLINA": "GASOLINA AGRUPADA",
            "GASOLINA ADITIVADA": "GASOLINA AGRUPADA",
        }
    )



# -------------------------------------------------
# Valor gasto Reais e Litros
# -------------------------------------------------
opcao_geral = st.segmented_control(
    "Visualização",
    options=["⛽ Total Geral", "🧩 Combustivel", "📊 Quantidade"],
    default="⛽ Total Geral",
)


if opcao_geral == "⛽ Total Geral":
    total_anual = (
        df
        .groupby(coluna_geral, as_index=False)
        .agg(valor=("valor_total", "sum"))
    )

    eixo_y = "valor"
    titulo_y = "Valor Total (R$)"
    cor = None
    titulo = "Evolução Mensal - Total Geral"

elif opcao_geral == "🧩 Combustivel":
    total_anual = (
        df
        .groupby(["combustivel_tipo", coluna_geral], as_index=False)
        .agg(valor=("valor_total", "sum"))
    )

    eixo_y = "valor"
    titulo_y = "Valor Total (R$)"
    cor = "combustivel_tipo"
    titulo = "Evolução Mensal por Combustível (R$)"

else:  # 📊 Quantidade
    total_anual = (
        df
        .groupby(["combustivel_tipo", coluna_geral], as_index=False)
        .agg(valor=("quantidade", "sum"))
    )

    eixo_y = "valor"
    titulo_y = "Litros abastecidos"
    cor = "combustivel_tipo"
    titulo = "Evolução Mensal por Combustível (Litros)"

fig = px.line(
    total_anual,
    x=coluna_geral,
    y=eixo_y,
    color=cor,
    markers=True,
    title=titulo,
)

fig.update_layout(
    xaxis_title=coluna_geral_nome,
    yaxis_title=titulo_y,
    legend_title_text="Combustível" if cor else None,
)

st.plotly_chart(fig, use_container_width=True)



# -------------------------------------------------
# Valor / Quantidade por Secretaria
# -------------------------------------------------
total_anual_secretaria = (
    df
    .groupby([coluna_geral, 'secretaria'], as_index=False)
    .agg(valor=('valor_total', 'sum'))
)

fig_secretaria = px.line(
    total_anual_secretaria,
    x=coluna_geral,
    y=eixo_y,
    color='secretaria',
    markers=True,
    title='Evolução Mensal por Secretaria (Valor Total)'
)

fig_secretaria.update_layout(
    xaxis_title=coluna_geral_nome,
    yaxis_title=titulo_y,
    legend_title_text='Secretaria',
)


fig_secretaria_pizza = px.line(
    total_anual_secretaria,
    x=coluna_geral,
    y=eixo_y,
    color='secretaria',
    markers=True,
    title='Evolução Mensal por Secretaria (Valor Total)'
)

fig_secretaria_pizza.update_layout(
    xaxis_title=coluna_geral_nome,
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
fig_litro = px.scatter(
    df,
    x='data_hora',
    y='valor_unitario',
    color='combustivel_tipo',
    title='Valor do combustivel por unidade'
)

fig_litro.update_layout(
    xaxis_title='Data Hora',
    yaxis_title='Valor por Litro'
)

st.plotly_chart(fig_litro, width="stretch")


# -------------------------------------------------
# Veículos por ano
# -------------------------------------------------
frota_evolucao = (
    df
    .groupby('ano', as_index=False)
    .agg(
        qtde_veiculos=('nome_veiculo', 'nunique'),
        valor_total=('valor_total', 'sum')
    )
)

# Gráfico base: quantidade de veículos
fig_evolucao = px.line(
    frota_evolucao,
    x="ano",
    y="qtde_veiculos",
    markers=True
)

# Linha de custo (segundo eixo)
fig_evolucao.add_scatter(
    x=frota_evolucao['ano'],
    y=frota_evolucao['valor_total'],
    mode='lines+markers',
    name='Valor Total (R$)',
    yaxis='y2'
)

fig_evolucao.update_layout(
    title='Veículos por Ano<br><sup>veículos únicos abastecidos durante o ano</sup>',
    xaxis_title='Ano',
    yaxis=dict(
        title='Quantidade de Veículos'
    ),
    yaxis2=dict(
        title='Valor Total (R$)',
        overlaying='y',
        side='right',
        tickformat=',.0f'
    ),
    legend_title_text=''
)

st.plotly_chart(fig_evolucao, use_container_width=True)

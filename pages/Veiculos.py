import streamlit as st
import pandas as pd
import plotly.express as px
from data.data import data
from plotly.subplots import make_subplots
import plotly.graph_objects as go


st.cache_data.clear()

df = data()


# -------------------------------------------------
# Filtrar período 💰
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



# -------------------------------------------------
# Configuração da página
# -------------------------------------------------
st.set_page_config(
    page_title="Veiculos - Combustível utilizado",
    page_icon="⛽",
    layout="wide"
)

st.title("⛽ Veiculos - Combustível utilizado")


id_veiculos = sorted(df["codigo_veiculo"].unique())

veiculo_selecionado = st.select_slider(
    "Selecione o ID do Veículo:",
    options=id_veiculos,
)

st.markdown(
    f"""
    **🚗 Veículos:** {len(id_veiculos):.0f}
    """,
    unsafe_allow_html=True,
)

total_mensal_veiculo = (
    df
    .groupby(
        ["codigo_veiculo", "nome_veiculo", "placa", "ano_mes"],
        as_index=False,
    )
    .agg(
        quantidade=("quantidade", "sum"),
        valor_total=("valor_total", "sum"),
    )
)



df_linhas = total_mensal_veiculo[
    total_mensal_veiculo['codigo_veiculo'] == veiculo_selecionado
]

titulo = (
    f"{df_linhas['codigo_veiculo'].iloc[0]} - "
    f"{df_linhas['nome_veiculo'].iloc[0]}"
    f"{df_linhas['placa'].iloc[0]}"
)

titulo_2 = (
    f"{df_linhas['placa'].iloc[0]}"
)

fig = px.line(
    df_linhas,
    x="ano_mes",
    y="quantidade",
    title=titulo,
    subtitle=f"Placa: {titulo_2}",
    )



st.plotly_chart(fig, use_container_width=True)




estatisticas_veiculo = (
    df
    .groupby(
        [
            "codigo_veiculo",
            "nome_veiculo",
        ],
        as_index=False,
    )
    .agg(
        media=("quantidade", "mean"),
        mediana=("quantidade", "median"),
        desvio_padrao=("quantidade", "std"),
        maximo=("quantidade", "max"),
        minimo=("quantidade", "min"),
        contagem=("quantidade", "count"),
    )
)

estatisticas_veiculo['cv'] = (
    estatisticas_veiculo['desvio_padrao'] /
    estatisticas_veiculo['media']
)

opcao_coluna = st.segmented_control(
    "Visualização",
    options=["Todos","Anomalias",],
    default="Todos",
)

if opcao_coluna == "Anomalias":
    estatisticas_veiculo = estatisticas_veiculo[
        estatisticas_veiculo['cv'] > 0.5
    ]
else:
    estatisticas_veiculo = estatisticas_veiculo


def classificar_cv(cv: float) -> str:
    if cv >= 0.5:
        return "🔴 Crítico"
    if cv >= 0.3:
        return "🟠 Alto"
    if cv >= 0.2:
        return "🟡 Atenção"
    return "🟢 Normal"

estatisticas_veiculo['nivel_risco'] = estatisticas_veiculo['cv'].apply(classificar_cv)

st.dataframe(estatisticas_veiculo, use_container_width=True)

xx = df[df['ano'] < 2030]["codigo_veiculo"].nunique()

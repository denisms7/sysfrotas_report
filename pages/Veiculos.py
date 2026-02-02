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

# -------------------------------------------------
# Estatísticas por veículo
# -------------------------------------------------
estatisticas_veiculo = (
    df
    .groupby(
        ["codigo_veiculo", "nome_veiculo"],
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

estatisticas_veiculo["cv"] = (
    estatisticas_veiculo["desvio_padrao"] /
    estatisticas_veiculo["media"]
)

def classificar_cv(cv: float) -> str:
    if cv >= 0.5:
        return "🔴 Crítico"
    if cv >= 0.3:
        return "🟠 Alto"
    if cv >= 0.2:
        return "🟡 Atenção"
    return "🟢 Normal"

estatisticas_veiculo["nivel_risco"] = (
    estatisticas_veiculo["cv"]
    .fillna(0)
    .apply(classificar_cv)
)

# -------------------------------------------------
# Filtro por nível de risco
# -------------------------------------------------
opcao_coluna = st.segmented_control(
    "Filtro por Nível de Risco",
    options=[
        "Todos",
        "🔴 Crítico",
        "🟠 Alto",
        "🟡 Atenção",
        "🟢 Normal",
    ],
    default="Todos",
)

if opcao_coluna != "Todos":
    estatisticas_veiculo = estatisticas_veiculo[
        estatisticas_veiculo["nivel_risco"] == opcao_coluna
    ]

# -------------------------------------------------
# DataFrame clicável
# -------------------------------------------------
selecao = st.dataframe(
    estatisticas_veiculo,
    use_container_width=True,
    selection_mode="single-row",
    on_select="rerun",
    key="tabela_veiculos",
)

# -------------------------------------------------
# Dados agregados para gráficos
# -------------------------------------------------
df_agrupado = (
    df
    .groupby(
        ["codigo_veiculo", "nome_veiculo", "ano_mes"],
        as_index=False,
    )
    .agg(
        quantidade=("quantidade", "sum"),
        valor_total=("valor_total", "sum"),
    )
)

# -------------------------------------------------
# Gráfico baseado no clique da tabela
# -------------------------------------------------
if selecao.selection.rows:
    idx = selecao.selection.rows[0]

    if idx >= len(estatisticas_veiculo):
        st.warning("Seleção desatualizada. Selecione novamente.")
        st.stop()

    linha = estatisticas_veiculo.iloc[idx]
    codigo_veiculo = linha["codigo_veiculo"]

    df_filtrado = df_agrupado[
        df_agrupado["codigo_veiculo"] == codigo_veiculo
    ]

    st.subheader(
        f"{linha['codigo_veiculo']} - {linha['nome_veiculo']}"
    )

    if df_filtrado.empty:
        st.warning(
            "Este veículo não possui dados no período selecionado."
        )
    else:
        fig = px.line(
            df_filtrado,
            x="ano_mes",
            y="quantidade",
            title="Evolução mensal do consumo",
            markers=True,
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Selecione um veículo na tabela para visualizar o gráfico.")

# -------------------------------------------------
# Seletor alternativo por ID (seguro)
# -------------------------------------------------
st.divider()

id_veiculos = sorted(df["codigo_veiculo"].unique())

veiculo_selecionado = st.select_slider(
    "Selecione o ID do Veículo",
    options=id_veiculos,
)

df_filtrado2 = df_agrupado[
    df_agrupado["codigo_veiculo"] == veiculo_selecionado
]

if df_filtrado2.empty:
    st.warning(
        "Este veículo não possui dados no período selecionado."
    )
else:
    nome_veiculo = df_filtrado2["nome_veiculo"].iloc[0]

    fig2 = px.line(
        df_filtrado2,
        x="ano_mes",
        y="quantidade",
        title=f"Consumo do veículo {nome_veiculo}",
        markers=True,
    )
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# Rodapé
# -------------------------------------------------
st.markdown(
    f"**🚗 Veículos no período:** {len(id_veiculos)}",
    unsafe_allow_html=True,
)

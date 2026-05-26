import streamlit as st
import plotly.express as px
from data.data import load_data_req

# -------------------------------------------------
# Configuracao da pagina
# -------------------------------------------------
st.set_page_config(
    page_title="Alertas de Consumo",
    page_icon="🚨",
    layout="wide",
)

st.title("🚨 Alertas de Consumo por Veiculo")

# -------------------------------------------------
# Carregamento dos dados
# -------------------------------------------------
with st.spinner("Carregando dados..."):
    df = load_data_req()

# -------------------------------------------------
# Filtros laterais
# -------------------------------------------------
st.sidebar.subheader("Configuracoes", divider=True)

LIMIAR = st.sidebar.segmented_control(
    "Limiar de alerta (%)",
    options=[10, 20, 30, 40],
    default=30,
    format_func=lambda x: f"{x}%",
)

meses_disponiveis = sorted(df["ano_mes"].unique())

if len(meses_disponiveis) < 2:
    st.warning("Dados insuficientes para comparacao. Sao necessarios pelo menos 2 meses de registros.")
    st.stop()

mes_selecionado = st.sidebar.selectbox(
    "Mes de referencia",
    options=meses_disponiveis[1:],
    index=len(meses_disponiveis) - 2,
    help="Mes cujo consumo sera analisado.",
)

idx = meses_disponiveis.index(mes_selecionado)

opcoes_comparacao = meses_disponiveis[:idx]

mes_anterior = st.sidebar.selectbox(
    "Mes de comparacao",
    options=opcoes_comparacao[::-1],
    index=0,
    help="Mes usado como base para calcular a variacao.",
)

st.sidebar.info(f"Comparando **{mes_selecionado}** com **{mes_anterior}**")

# -------------------------------------------------
# Agregacao por veiculo nos dois meses
# -------------------------------------------------
df_atual = (
    df[df["ano_mes"] == mes_selecionado]
    .groupby(["codigo_veiculo", "nome_veiculo"], as_index=False)
    .agg(
        litros_atual=("quantidade", "sum"),
        valor_atual=("valor_total", "sum"),
    )
)

df_ant = (
    df[df["ano_mes"] == mes_anterior]
    .groupby(["codigo_veiculo", "nome_veiculo"], as_index=False)
    .agg(
        litros_anterior=("quantidade", "sum"),
        valor_anterior=("valor_total", "sum"),
    )
)

df_comp = df_atual.merge(
    df_ant[["codigo_veiculo", "litros_anterior", "valor_anterior"]],
    on="codigo_veiculo",
    how="inner",
)

df_comp = df_comp[
    (df_comp["litros_anterior"] > 0) & (df_comp["valor_anterior"] > 0)
]

# -------------------------------------------------
# Calcula variacao percentual
# -------------------------------------------------
df_comp["var_litros"] = (
    (df_comp["litros_atual"] - df_comp["litros_anterior"])
    / df_comp["litros_anterior"]
    * 100
)

df_comp["var_valor"] = (
    (df_comp["valor_atual"] - df_comp["valor_anterior"])
    / df_comp["valor_anterior"]
    * 100
)

# -------------------------------------------------
# Filtra alertas
# -------------------------------------------------
df_alertas = df_comp[
    (df_comp["var_litros"] >= LIMIAR) | (df_comp["var_valor"] >= LIMIAR)
].sort_values("var_litros", ascending=False)

# -------------------------------------------------
# Metricas de resumo
# -------------------------------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Veiculos monitorados", len(df_comp))

col2.metric(
    "🚨 Alertas gerados",
    len(df_alertas),
    delta=f"+{LIMIAR}% limiar",
    delta_color="inverse",
)

col3.metric("Periodo", f"{mes_anterior}  ->  {mes_selecionado}")

st.divider()

# -------------------------------------------------
# Resultado dos alertas
# -------------------------------------------------
if df_alertas.empty:
    st.success(
        f"Nenhum veiculo com aumento acima de {LIMIAR}% "
        f"entre {mes_anterior} e {mes_selecionado}."
    )
    st.stop()

st.subheader(f"⚠️ {len(df_alertas)} veiculo(s) com aumento acima de {LIMIAR}%")

df_exibicao = df_alertas[
    [
        "codigo_veiculo",
        "nome_veiculo",
        "litros_anterior",
        "litros_atual",
        "var_litros",
        "valor_anterior",
        "valor_atual",
        "var_valor",
    ]
].rename(
    columns={
        "codigo_veiculo": "ID",
        "nome_veiculo": "Veiculo",
        "litros_anterior": f"Litros {mes_anterior}",
        "litros_atual": f"Litros {mes_selecionado}",
        "var_litros": "Var. Litros (%)",
        "valor_anterior": f"R$ {mes_anterior}",
        "valor_atual": f"R$ {mes_selecionado}",
        "var_valor": "Var. R$ (%)",
    }
)

st.dataframe(df_exibicao, width="stretch")

st.divider()

# -------------------------------------------------
# Grafico variacao de litros
# -------------------------------------------------
top_litros = df_alertas.sort_values("var_litros", ascending=False).head(20)

fig_litros = px.bar(
    top_litros,
    x="nome_veiculo",
    y="var_litros",
    color="var_litros",
    color_continuous_scale="Reds",
    text_auto=".1f",
    title=f"Variacao de Litros por Veiculo (%) — {mes_anterior} vs {mes_selecionado}",
    custom_data=["litros_anterior", "litros_atual", "nome_veiculo"],
)

fig_litros.update_traces(
    hovertemplate=(
        "<b>%{customdata[2]}</b><br>"
        f"{mes_anterior}: %{{customdata[0]:,.1f}} L<br>"
        f"{mes_selecionado}: %{{customdata[1]:,.1f}} L<br>"
        "Variacao: <b>%{y:.1f}%</b>"
        "<extra></extra>"
    )
)

fig_litros.add_hline(
    y=LIMIAR,
    line_dash="dash",
    line_color="orange",
    annotation_text=f"Limiar {LIMIAR}%",
    annotation_position="top right",
)

fig_litros.update_layout(
    xaxis_title="Veiculo",
    yaxis_title="Variacao de Litros (%)",
    coloraxis_showscale=False,
)

st.plotly_chart(fig_litros, width="stretch")

# -------------------------------------------------
# Grafico variacao de valor R$
# -------------------------------------------------
top_valor = df_alertas.sort_values("var_valor", ascending=False).head(20)

fig_valor = px.bar(
    top_valor,
    x="nome_veiculo",
    y="var_valor",
    color="var_valor",
    color_continuous_scale="Oranges",
    text_auto=".1f",
    title=f"Variacao de Valor (R$) por Veiculo (%) — {mes_anterior} vs {mes_selecionado}",
    custom_data=["valor_anterior", "valor_atual", "nome_veiculo"],
)

fig_valor.update_traces(
    hovertemplate=(
        "<b>%{customdata[2]}</b><br>"
        f"{mes_anterior}: R$ %{{customdata[0]:,.2f}}<br>"
        f"{mes_selecionado}: R$ %{{customdata[1]:,.2f}}<br>"
        "Variacao: <b>%{y:.1f}%</b>"
        "<extra></extra>"
    )
)

fig_valor.add_hline(
    y=LIMIAR,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Limiar {LIMIAR}%",
    annotation_position="top right",
)

fig_valor.update_layout(
    xaxis_title="Veiculo",
    yaxis_title="Variacao de Valor R$ (%)",
    coloraxis_showscale=False,
)

st.plotly_chart(fig_valor, width="stretch")

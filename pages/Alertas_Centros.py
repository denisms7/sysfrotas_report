import streamlit as st
import plotly.express as px
from data.data import load_data_req

# -------------------------------------------------
# Configuracao da pagina
# -------------------------------------------------
st.set_page_config(
    page_title="Alertas por Centro de Custo",
    page_icon="🏢",
    layout="wide",
)

st.title("🏢 Alertas de Consumo por Centro de Custo")

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
    options=[5, 15, 35],
    default=15,
    format_func=lambda x: f"{x}%",
)

meses_disponiveis = sorted(df["ano_mes"].unique())

if len(meses_disponiveis) < 2:
    st.warning("Dados insuficientes para comparacao. Sao necessarios pelo menos 2 meses de registros.")
    st.stop()

_opcoes_mes = meses_disponiveis[1:]
mes_selecionado = st.sidebar.selectbox(
    "Mes de referencia",
    options=_opcoes_mes,
    index=len(_opcoes_mes) - 1,
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
# Helpers: agrega e calcula variacao
# -------------------------------------------------
def calcular_variacao(df_ref, df_ant, grupo):
    atual = (
        df_ref
        .groupby(grupo, as_index=False)
        .agg(litros_atual=("quantidade", "sum"), valor_atual=("valor_total", "sum"))
    )
    anterior = (
        df_ant
        .groupby(grupo, as_index=False)
        .agg(litros_anterior=("quantidade", "sum"), valor_anterior=("valor_total", "sum"))
    )
    comp = atual.merge(anterior, on=grupo, how="inner")
    comp = comp[(comp["litros_anterior"] > 0) & (comp["valor_anterior"] > 0)]
    comp["var_litros"] = (comp["litros_atual"] - comp["litros_anterior"]) / comp["litros_anterior"] * 100
    comp["var_valor"]  = (comp["valor_atual"]  - comp["valor_anterior"])  / comp["valor_anterior"]  * 100
    return comp


def filtrar_alertas(comp):
    return comp[
        (comp["var_litros"] >= LIMIAR) | (comp["var_valor"] >= LIMIAR)
    ].sort_values("var_litros", ascending=False)


def exibir_tabela(df_alertas, grupo_label):
    col_nome = grupo_label
    df_exib = df_alertas.rename(columns={
        col_nome:         col_nome,
        "litros_anterior": f"Litros {mes_anterior}",
        "litros_atual":    f"Litros {mes_selecionado}",
        "var_litros":      "Var. Litros (%)",
        "valor_anterior":  f"R$ {mes_anterior}",
        "valor_atual":     f"R$ {mes_selecionado}",
        "var_valor":       "Var. R$ (%)",
    })
    cols = [col_nome,
            f"Litros {mes_anterior}", f"Litros {mes_selecionado}", "Var. Litros (%)",
            f"R$ {mes_anterior}",     f"R$ {mes_selecionado}",     "Var. R$ (%)"]
    st.dataframe(df_exib[cols], width="stretch")


def exibir_grafico_litros(df_alertas, x_col, titulo):
    top = df_alertas.sort_values("var_litros", ascending=False).head(20)
    fig = px.bar(
        top,
        x=x_col,
        y="var_litros",
        color="var_litros",
        color_continuous_scale="Reds",
        text_auto=".1f",
        title=titulo,
        custom_data=["litros_anterior", "litros_atual", x_col],
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[2]}</b><br>"
            f"{mes_anterior}: %{{customdata[0]:,.1f}} L<br>"
            f"{mes_selecionado}: %{{customdata[1]:,.1f}} L<br>"
            "Variacao: <b>%{y:.1f}%</b>"
            "<extra></extra>"
        )
    )
    fig.add_hline(y=LIMIAR, line_dash="dash", line_color="orange",
                  annotation_text=f"Limiar {LIMIAR}%", annotation_position="top right")
    fig.update_layout(xaxis_title=x_col, yaxis_title="Variacao de Litros (%)", coloraxis_showscale=False)
    st.plotly_chart(fig, width="stretch")


def exibir_grafico_valor(df_alertas, x_col, titulo):
    top = df_alertas.sort_values("var_valor", ascending=False).head(20)
    fig = px.bar(
        top,
        x=x_col,
        y="var_valor",
        color="var_valor",
        color_continuous_scale="Oranges",
        text_auto=".1f",
        title=titulo,
        custom_data=["valor_anterior", "valor_atual", x_col],
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[2]}</b><br>"
            f"{mes_anterior}: R$ %{{customdata[0]:,.2f}}<br>"
            f"{mes_selecionado}: R$ %{{customdata[1]:,.2f}}<br>"
            "Variacao: <b>%{y:.1f}%</b>"
            "<extra></extra>"
        )
    )
    fig.add_hline(y=LIMIAR, line_dash="dash", line_color="red",
                  annotation_text=f"Limiar {LIMIAR}%", annotation_position="top right")
    fig.update_layout(xaxis_title=x_col, yaxis_title="Variacao de Valor R$ (%)", coloraxis_showscale=False)
    st.plotly_chart(fig, width="stretch")


# -------------------------------------------------
# Dados dos dois meses
# -------------------------------------------------
df_ref = df[df["ano_mes"] == mes_selecionado]
df_ant = df[df["ano_mes"] == mes_anterior]

# -------------------------------------------------
# NIVEL 1 — Por Secretaria
# -------------------------------------------------
st.subheader("Por Secretaria")

comp_sec = calcular_variacao(df_ref, df_ant, "secretaria")
alertas_sec = filtrar_alertas(comp_sec)

col1, col2 = st.columns(2)
col1.metric("Secretarias monitoradas", len(comp_sec))
col2.metric("🚨 Alertas", len(alertas_sec))

if alertas_sec.empty:
    st.success(f"Nenhuma secretaria com aumento acima de {LIMIAR}% no periodo.")
else:
    st.caption(f"⚠️ {len(alertas_sec)} secretaria(s) com aumento acima de {LIMIAR}%")
    exibir_tabela(alertas_sec, "secretaria")
    col_a, col_b = st.columns(2)
    with col_a:
        exibir_grafico_litros(
            alertas_sec, "secretaria",
            f"Variacao de Litros por Secretaria (%) — {mes_anterior} vs {mes_selecionado}"
        )
    with col_b:
        exibir_grafico_valor(
            alertas_sec, "secretaria",
            f"Variacao de Valor R$ por Secretaria (%) — {mes_anterior} vs {mes_selecionado}"
        )

st.divider()

# -------------------------------------------------
# NIVEL 2 — Por Centro de Custo
# -------------------------------------------------
st.subheader("Por Centro de Custo")

# Filtro opcional por secretaria
secretarias = sorted(df["secretaria"].dropna().unique())
sec_filtro = st.multiselect(
    "Filtrar por secretaria (opcional)",
    options=secretarias,
    default=[],
    placeholder="Todas as secretarias",
)

if sec_filtro:
    df_ref_cc = df_ref[df_ref["secretaria"].isin(sec_filtro)]
    df_ant_cc = df_ant[df_ant["secretaria"].isin(sec_filtro)]
else:
    df_ref_cc = df_ref
    df_ant_cc = df_ant

comp_cc = calcular_variacao(df_ref_cc, df_ant_cc, "centro_de_custos")
alertas_cc = filtrar_alertas(comp_cc)

col3, col4 = st.columns(2)
col3.metric("Centros de custo monitorados", len(comp_cc))
col4.metric("🚨 Alertas", len(alertas_cc))

if alertas_cc.empty:
    st.success(f"Nenhum centro de custo com aumento acima de {LIMIAR}% no periodo.")
else:
    st.caption(f"⚠️ {len(alertas_cc)} centro(s) de custo com aumento acima de {LIMIAR}%")
    exibir_tabela(alertas_cc, "centro_de_custos")
    exibir_grafico_litros(
        alertas_cc, "centro_de_custos",
        f"Variacao de Litros por Centro de Custo (%) — {mes_anterior} vs {mes_selecionado}"
    )
    exibir_grafico_valor(
        alertas_cc, "centro_de_custos",
        f"Variacao de Valor R$ por Centro de Custo (%) — {mes_anterior} vs {mes_selecionado}"
    )

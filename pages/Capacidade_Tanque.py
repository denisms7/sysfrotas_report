import streamlit as st
import pandas as pd
import plotly.express as px
from data.data import load_data_req
from pathlib import Path

# -------------------------------------------------
# Configuracao da pagina
# -------------------------------------------------
st.set_page_config(
    page_title="Abastecimento Acima da Capacidade",
    page_icon="⚠️",
    layout="wide",
)

st.title("⛽ Abastecimento Acima da Capacidade do Tanque")
st.caption("Detecta requisicoes onde a quantidade abastecida supera a capacidade do tanque do veiculo.")

# -------------------------------------------------
# Carregamento dos dados
# -------------------------------------------------
with st.spinner("Carregando dados..."):
    df = load_data_req()

base_dir = Path(__file__).resolve().parent.parent / "data"
df_cap = pd.read_csv(base_dir / "capacidade_tanques.csv", sep=";")

df = df.merge(df_cap[["codigo_veiculo", "capacidade_litros"]], on="codigo_veiculo", how="left")

# -------------------------------------------------
# Filtros
# -------------------------------------------------
st.sidebar.subheader("⚙️ Filtros", divider=True)

anos = sorted(df["ano"].dropna().unique())
ano_inicio, ano_fim = st.sidebar.select_slider(
    "Intervalo de anos",
    options=anos,
    value=(2024, int(df["ano"].max())),
)

tolerancia = st.sidebar.slider(
    "Tolerancia acima da capacidade (%)",
    min_value=0,
    max_value=30,
    value=5,
    step=1,
    help="Permite uma margem para arredondamentos. 0% = qualquer valor acima ja e alerta.",
)

df = df.loc[(df["ano"] >= ano_inicio) & (df["ano"] <= ano_fim)].copy()

# -------------------------------------------------
# Detectar abastecimentos suspeitos
# -------------------------------------------------
df_com_cap = df[df["capacidade_litros"].notna()].copy()
df_sem_cap = df[df["capacidade_litros"].isna()].copy()

limiar = df_com_cap["capacidade_litros"] * (1 + tolerancia / 100)
df_suspeitos = df_com_cap[df_com_cap["quantidade"] > limiar].copy()
df_suspeitos["excesso_litros"] = (df_suspeitos["quantidade"] - df_suspeitos["capacidade_litros"]).round(2)
df_suspeitos["excesso_pct"] = ((df_suspeitos["quantidade"] / df_suspeitos["capacidade_litros"] - 1) * 100).round(1)
df_suspeitos = df_suspeitos.sort_values("excesso_pct", ascending=False)

# -------------------------------------------------
# Metricas de resumo
# -------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de requisicoes", f"{len(df_com_cap):,}")
col2.metric("🚨 Suspeitas", f"{len(df_suspeitos):,}")
col3.metric("Veiculos envolvidos", df_suspeitos["codigo_veiculo"].nunique())
col4.metric("Valor total suspeito (R$)", f"R$ {df_suspeitos['valor_total'].sum():,.2f}")

st.divider()

if df_sem_cap.shape[0] > 0:
    st.info(f"ℹ️ {df_sem_cap['codigo_veiculo'].nunique()} veiculo(s) sem capacidade cadastrada foram ignorados.")

# -------------------------------------------------
# Tabela de suspeitos
# -------------------------------------------------
if df_suspeitos.empty:
    st.success(f"Nenhum abastecimento acima da capacidade (tolerancia: {tolerancia}%).")
    st.stop()

st.subheader(f"🚨 {len(df_suspeitos)} requisicao(oes) suspeitas")

colunas = {
    "data_hora":          "Data/Hora",
    "codigo_veiculo":     "ID Veiculo",
    "nome_veiculo":       "Veiculo",
    "placa":              "Placa",
    "combustivel_tipo":   "Combustivel",
    "quantidade":         "Litros Abast.",
    "capacidade_litros":  "Cap. Tanque (L)",
    "excesso_litros":     "Excesso (L)",
    "excesso_pct":        "Excesso (%)",
    "valor_total":        "Valor (R$)",
    "documento_fiscal":   "Doc. Fiscal",
}

df_exib = (
    df_suspeitos[list(colunas.keys())]
    .rename(columns=colunas)
    .sort_values("Excesso (%)", ascending=False)
)

st.dataframe(df_exib, width="stretch")

# Exportar
csv = df_exib.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
st.download_button(
    label="⬇️ Exportar como CSV",
    data=csv,
    file_name=f"abastecimentos_suspeitos_{ano_inicio}_{ano_fim}.csv",
    mime="text/csv",
)

st.divider()

# -------------------------------------------------
# Grafico: veiculos com mais ocorrencias
# -------------------------------------------------
ocorrencias = (
    df_suspeitos
    .groupby(["codigo_veiculo", "nome_veiculo"], as_index=False)
    .agg(
        ocorrencias=("quantidade", "count"),
        excesso_total=("excesso_litros", "sum"),
        excesso_max_pct=("excesso_pct", "max"),
    )
    .sort_values("ocorrencias", ascending=False)
    .head(20)
)

col_a, col_b = st.columns(2)

with col_a:
    fig1 = px.bar(
        ocorrencias,
        x="nome_veiculo",
        y="ocorrencias",
        color="ocorrencias",
        color_continuous_scale="Reds",
        text_auto=True,
        title="Veiculos com mais ocorrencias suspeitas",
        custom_data=["codigo_veiculo", "excesso_total", "excesso_max_pct"],
    )
    fig1.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "ID: %{customdata[0]}<br>"
            "Ocorrencias: %{y}<br>"
            "Excesso total: %{customdata[1]:,.1f} L<br>"
            "Maior excesso: %{customdata[2]:.1f}%"
            "<extra></extra>"
        )
    )
    fig1.update_layout(xaxis_title="Veiculo", yaxis_title="Qtde ocorrencias", coloraxis_showscale=False)
    st.plotly_chart(fig1, width="stretch")

with col_b:
    fig2 = px.bar(
        ocorrencias.sort_values("excesso_total", ascending=False),
        x="nome_veiculo",
        y="excesso_total",
        color="excesso_total",
        color_continuous_scale="Oranges",
        text_auto=".1f",
        title="Veiculos com maior excesso acumulado (Litros)",
        custom_data=["codigo_veiculo", "ocorrencias"],
    )
    fig2.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "ID: %{customdata[0]}<br>"
            "Excesso total: %{y:,.1f} L<br>"
            "Ocorrencias: %{customdata[1]}"
            "<extra></extra>"
        )
    )
    fig2.update_layout(xaxis_title="Veiculo", yaxis_title="Excesso acumulado (L)", coloraxis_showscale=False)
    st.plotly_chart(fig2, width="stretch")

# -------------------------------------------------
# Evolucao temporal
# -------------------------------------------------
evolucao = (
    df_suspeitos
    .groupby("ano_mes", as_index=False)
    .agg(ocorrencias=("quantidade", "count"), excesso_total=("excesso_litros", "sum"))
)

fig3 = px.bar(
    evolucao,
    x="ano_mes",
    y="ocorrencias",
    title="Evolucao mensal de ocorrencias suspeitas",
    text_auto=True,
    custom_data=["excesso_total"],
)
fig3.update_traces(
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Ocorrencias: %{y}<br>"
        "Excesso total: %{customdata[0]:,.1f} L"
        "<extra></extra>"
    )
)
fig3.update_layout(xaxis_title="Mes", yaxis_title="Qtde ocorrencias")
st.plotly_chart(fig3, width="stretch")

import streamlit as st
from data.data import load_data_req

# -------------------------------------------------
# Configuracao da pagina
# -------------------------------------------------
st.set_page_config(
    page_title="Litros por Requisicoes",
    page_icon="⛽",
    layout="wide",
)

st.title("⛽ Litros por Requisicoes")

# -------------------------------------------------
# Carregamento dos dados
# -------------------------------------------------
with st.spinner("Carregando dados..."):
    df = load_data_req()

# -------------------------------------------------
# Filtros — todos na sidebar
# -------------------------------------------------
st.sidebar.subheader("🎯 Filtros", divider=True)

# Filtro de ano
ano_min = int(df["ano"].min())
ano_max = int(df["ano"].max())

ano_inicio, ano_fim = st.sidebar.slider(
    "Intervalo de anos",
    min_value=ano_min,
    max_value=ano_max,
    value=(ano_min, ano_max),
    step=1,
)

df = df.loc[
    (df["ano"] >= ano_inicio) &
    (df["ano"] <= ano_fim)
].copy()

# Filtro de litros
req_min = int(df["quantidade"].min())
req_max = int(df["quantidade"].max())

req_inicio, req_fim = st.sidebar.slider(
    "Quantidade de litros",
    min_value=req_min,
    max_value=req_max,
    value=(req_min, req_max),
    step=10,
)

# Filtro por tipo de combustivel
tipos_disponiveis = sorted(df["combustivel_tipo"].dropna().unique())
tipos_selecionados = st.sidebar.multiselect(
    "Tipo de combustivel",
    options=tipos_disponiveis,
    default=tipos_disponiveis,
    placeholder="Selecione os tipos...",
)

# Filtro por veiculo ou placa
busca_veiculo = st.sidebar.text_input(
    "Buscar por veiculo ou placa",
    placeholder="Ex: AMBULANCIA ou ABC-1234",
).strip().upper()

# -------------------------------------------------
# Aplicar filtros
# -------------------------------------------------
df_req = df.loc[
    (df["quantidade"] >= req_inicio) &
    (df["quantidade"] <= req_fim) &
    (df["combustivel_tipo"].isin(tipos_selecionados))
].copy()

if busca_veiculo:
    df_req = df_req.loc[
        df_req["nome_veiculo"].str.upper().str.contains(busca_veiculo, na=False) |
        df_req["placa"].str.upper().str.contains(busca_veiculo, na=False)
    ]

# Ordenar por data decrescente
df_req = df_req.sort_values("data_hora", ascending=False)

# -------------------------------------------------
# Contagem
# -------------------------------------------------
st.markdown(f"**Requisicoes no periodo:** {len(df_req)}")

# -------------------------------------------------
# Tabela
# -------------------------------------------------
colunas_exibicao = {
    "documento_fiscal":   "Doc. Fiscal",
    "codigo_abastecimento": "Cod. Requisicao",
    "data_hora":          "Data/Hora",
    "codigo_veiculo":     "ID Veiculo",
    "nome_veiculo":       "Veiculo",
    "placa":              "Placa",
    "combustivel_tipo":   "Tipo Combustivel",
    "quantidade":         "Litros",
    "valor_unitario":     "R$/Litro",
    "valor_total":        "Valor Total (R$)",
}

df_exibicao = (
    df_req[list(colunas_exibicao.keys())]
    .rename(columns=colunas_exibicao)
)

st.dataframe(df_exibicao, width="stretch")

# -------------------------------------------------
# Exportar CSV
# -------------------------------------------------
csv = df_exibicao.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")

st.download_button(
    label="⬇️ Exportar tabela como CSV",
    data=csv,
    file_name=f"requisicoes_{ano_inicio}_{ano_fim}.csv",
    mime="text/csv",
)

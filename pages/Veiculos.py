import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data.data import load_data_req

# -------------------------------------------------
# Configuracao da pagina
# -------------------------------------------------
st.set_page_config(
    page_title="Veiculos Individuais",
    page_icon="🚗",
    layout="wide",
)

st.title("🚗 Veiculos Individuais")

# -------------------------------------------------
# Carregamento dos dados
# -------------------------------------------------
with st.spinner("Carregando dados..."):
    df = load_data_req()

# -------------------------------------------------
# Filtros na sidebar
# -------------------------------------------------
st.sidebar.subheader("🎯 Filtros", divider=True)

ano_min = int(df["ano"].min())
ano_max = int(df["ano"].max())

ano_inicio, ano_fim = st.sidebar.slider(
    "Intervalo de anos",
    min_value=ano_min,
    max_value=ano_max,
    value=(2024, ano_max),
    step=1,
)

df = df.loc[(df["ano"] >= ano_inicio) & (df["ano"] <= ano_fim)].copy()

# Filtro por secretaria
secretarias = ["Todas"] + sorted(df["secretaria"].dropna().unique().tolist())
secretaria_sel = st.sidebar.selectbox("Secretaria", options=secretarias)

if secretaria_sel != "Todas":
    df = df[df["secretaria"] == secretaria_sel].copy()

# -------------------------------------------------
# Estatisticas por veiculo
# -------------------------------------------------
estatisticas_veiculo = (
    df
    .groupby(["codigo_veiculo", "nome_veiculo"], as_index=False)
    .agg(
        media=("quantidade", "mean"),
        mediana=("quantidade", "median"),
        desvio_padrao=("quantidade", "std"),
        maximo=("quantidade", "max"),
        minimo=("quantidade", "min"),
        contagem=("quantidade", "count"),
        valor_total=("valor_total", "sum"),
    )
)

estatisticas_veiculo["cv"] = (
    estatisticas_veiculo["desvio_padrao"] / estatisticas_veiculo["media"]
)

def classificar_cv(cv: float) -> str:
    if cv >= 0.5:
        return "🔴 Critico"
    if cv >= 0.3:
        return "🟠 Alto"
    if cv >= 0.2:
        return "🟡 Atencao"
    return "🟢 Normal"

estatisticas_veiculo["nivel_risco"] = (
    estatisticas_veiculo["cv"].fillna(0).apply(classificar_cv)
)

# -------------------------------------------------
# Filtro por nivel de risco
# -------------------------------------------------
opcao_risco = st.segmented_control(
    "Filtro por Nivel de Risco",
    options=["Todos", "🔴 Critico", "🟠 Alto", "🟡 Atencao", "🟢 Normal"],
    default="Todos",
)

if opcao_risco != "Todos":
    estatisticas_veiculo = estatisticas_veiculo[
        estatisticas_veiculo["nivel_risco"] == opcao_risco
    ]

# -------------------------------------------------
# Scatter de risco: Media x CV
# -------------------------------------------------
st.divider()
st.subheader("Mapa de Risco da Frota")

fig_scatter = px.scatter(
    estatisticas_veiculo,
    x="media",
    y="cv",
    color="nivel_risco",
    size="contagem",
    hover_name="nome_veiculo",
    custom_data=["codigo_veiculo", "contagem", "valor_total"],
    title="Media de Litros vs Coeficiente de Variacao (CV) — tamanho = n° de abastecimentos",
    color_discrete_map={
        "🔴 Critico":  "#e74c3c",
        "🟠 Alto":     "#e67e22",
        "🟡 Atencao":  "#f1c40f",
        "🟢 Normal":   "#2ecc71",
    },
)

fig_scatter.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "ID: %{customdata[0]}<br>"
        "Media: %{x:.1f} L<br>"
        "CV: %{y:.2f}<br>"
        "Abastecimentos: %{customdata[1]}<br>"
        "Total gasto: R$ %{customdata[2]:,.2f}"
        "<extra></extra>"
    )
)

fig_scatter.add_hline(y=0.5, line_dash="dash", line_color="#e74c3c",
                      annotation_text="Critico (CV=0.5)", annotation_position="top right")
fig_scatter.add_hline(y=0.3, line_dash="dash", line_color="#e67e22",
                      annotation_text="Alto (CV=0.3)", annotation_position="top right")
fig_scatter.add_hline(y=0.2, line_dash="dot", line_color="#f1c40f",
                      annotation_text="Atencao (CV=0.2)", annotation_position="top right")

fig_scatter.update_layout(
    xaxis_title="Media de Litros por Abastecimento",
    yaxis_title="Coeficiente de Variacao (CV)",
    legend_title="Nivel de Risco",
)

st.plotly_chart(fig_scatter, width="stretch")


# -------------------------------------------------
# Tabela com colunas renomeadas
# -------------------------------------------------
tabela_exibicao = estatisticas_veiculo.rename(columns={
    "codigo_veiculo":  "ID",
    "nome_veiculo":    "Veiculo",
    "media":           "Media (L)",
    "mediana":         "Mediana (L)",
    "desvio_padrao":   "Desvio Padrao",
    "maximo":          "Max (L)",
    "minimo":          "Min (L)",
    "contagem":        "Abastecimentos",
    "valor_total":     "Total Gasto (R$)",
    "cv":              "CV",
    "nivel_risco":     "Risco",
})

selecao = st.dataframe(
    tabela_exibicao,
    width="stretch",
    selection_mode="single-row",
    on_select="rerun",
    key="tabela_veiculos",
)

st.caption("Clique em um veiculo para ver o historico detalhado abaixo.")


# -------------------------------------------------
# Historico do veiculo selecionado na tabela
# -------------------------------------------------
df_agrupado = (
    df
    .groupby(["codigo_veiculo", "nome_veiculo", "ano_mes"], as_index=False)
    .agg(
        quantidade=("quantidade", "sum"),
        valor_total=("valor_total", "sum"),
    )
)

if selecao.selection.rows:
    idx = selecao.selection.rows[0]

    if idx >= len(estatisticas_veiculo):
        st.warning("Selecao desatualizada. Selecione novamente.")
        st.stop()

    linha = estatisticas_veiculo.iloc[idx]
    codigo_veiculo = linha["codigo_veiculo"]
    nome_veiculo = linha["nome_veiculo"]

    df_filtrado = df_agrupado[df_agrupado["codigo_veiculo"] == codigo_veiculo]

    st.divider()
    st.subheader(f"ID {int(codigo_veiculo)} — {nome_veiculo}")

    if df_filtrado.empty:
        st.warning("Este veiculo nao possui dados no periodo selecionado.")
    else:
        # Segmented control para alternar entre litros e R$
        metrica = st.segmented_control(
            "Visualizar",
            options=["Litros", "Valor R$", "Ambos"],
            default="Ambos",
        )

        if metrica == "Ambos":
            fig_hist = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                subplot_titles=("Litros abastecidos", "Valor gasto (R$)"),
                vertical_spacing=0.12,
            )
            fig_hist.add_trace(
                go.Scatter(
                    x=df_filtrado["ano_mes"],
                    y=df_filtrado["quantidade"],
                    mode="lines+markers",
                    name="Litros",
                    line=dict(color="#3498db"),
                    hovertemplate="<b>%{x}</b><br>Litros: %{y:,.1f}<extra></extra>",
                ),
                row=1, col=1,
            )
            fig_hist.add_trace(
                go.Scatter(
                    x=df_filtrado["ano_mes"],
                    y=df_filtrado["valor_total"],
                    mode="lines+markers",
                    name="R$",
                    line=dict(color="#e67e22"),
                    hovertemplate="<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>",
                ),
                row=2, col=1,
            )
            fig_hist.update_layout(
                height=500,
                title_text=f"Historico mensal — {nome_veiculo}",
                showlegend=False,
            )
            fig_hist.update_yaxes(title_text="Litros", row=1, col=1)
            fig_hist.update_yaxes(title_text="R$", row=2, col=1)
            st.plotly_chart(fig_hist, width="stretch")

        elif metrica == "Litros":
            fig_l = px.line(
                df_filtrado, x="ano_mes", y="quantidade",
                title=f"Litros mensais — {nome_veiculo}",
                markers=True,
            )
            fig_l.update_traces(
                hovertemplate="<b>%{x}</b><br>Litros: %{y:,.1f}<extra></extra>"
            )
            fig_l.update_layout(xaxis_title="Mes", yaxis_title="Litros")
            st.plotly_chart(fig_l, width="stretch")

        else:
            fig_v = px.line(
                df_filtrado, x="ano_mes", y="valor_total",
                title=f"Valor gasto mensal (R$) — {nome_veiculo}",
                markers=True,
                color_discrete_sequence=["#e67e22"],
            )
            fig_v.update_traces(
                hovertemplate="<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>"
            )
            fig_v.update_layout(xaxis_title="Mes", yaxis_title="R$")
            st.plotly_chart(fig_v, width="stretch")

else:
    st.info("Selecione um veiculo na tabela acima para ver o historico.")

# -------------------------------------------------
# Rodape
# -------------------------------------------------
st.divider()
st.caption(f"🚗 Veiculos no periodo: {estatisticas_veiculo['codigo_veiculo'].nunique()}")

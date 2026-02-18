import streamlit as st
import pandas as pd
import plotly.express as px
from data.data import load_data_req
from plotly.subplots import make_subplots
import plotly.graph_objects as go


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
# Carregamento dos dados
# -------------------------------------------------
with st.spinner("Carregando dados..."):
    df = load_data_req()


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


st.subheader(f"Fonte de dados SysFrotas: {ano_min} a {ano_max}")

st.markdown(
    f"""
    **Registros:** {len(df):.0f}<br>
    **Registros com valor total zero:** {len(df[df['valor_total'] == 0]):.0f}
    """,
    unsafe_allow_html=True,
)


col1, col2, col3, col4 = st.columns(4)

df_abastecimentos = df[df['valor_total'] > 0]

media_litros = df_abastecimentos['quantidade'].mean()

moda_series = df_abastecimentos['quantidade'].mode()
moda_litros = moda_series.iloc[0] if not moda_series.empty else 0

max_litros = df_abastecimentos['quantidade'].max()
min_litros = df_abastecimentos['quantidade'].min()

col1.metric(
    "Média de litros por requisição",
    f"{media_litros:.2f} L",
)

col2.metric(
    "Moda de litros por requisição",
    f"{moda_litros:.2f} L",
)

col3.metric(
    "Abastecimento máximo",
    f"{max_litros:.2f} L",
)

col4.metric(
    "Abastecimento mínimo",
    f"{min_litros:.2f} L",
)








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
    "Agrupar Gasolina Comum e Aditivada",
    options=["Separar", "Agrupar"],
    default="Separar",
)


st.sidebar.info("Os Agrupamentos somam o valor total e litros dos tipos selecionados.")

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
# Valor gasto GLOBAL
# -------------------------------------------------
opcao_geral = st.segmented_control(
    "Visualização",
    options=["Total Geral", "Combustivel R$", "Combustivel Quantidade"],
    default="Total Geral",
)


if opcao_geral == "Total Geral":
    total_anual = (
        df
        .groupby(coluna_geral, as_index=False)
        .agg(valor=("valor_total", "sum"))
    )

    eixo_y = "valor"
    titulo_y = "Valor Total (R$)"
    cor = None
    titulo = "Evolução Mensal - Total Geral"

elif opcao_geral == "Combustivel R$":
    total_anual = (
        df
        .groupby(["combustivel_tipo", coluna_geral], as_index=False)
        .agg(valor=("valor_total", "sum"))
    )

    eixo_y = "valor"
    titulo_y = "Valor Total (R$)"
    cor = "combustivel_tipo"
    titulo = "Evolução Mensal por Combustível (R$)"

elif opcao_geral == "Combustivel Quantidade":
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

st.plotly_chart(fig, width='stretch')



# --------------------------------------------------------------------------------------------------
# Valor / Quantidade por Secretaria
# --------------------------------------------------------------------------------------------------
total_anual_secretaria = (
    df
    .groupby([coluna_geral, 'secretaria'], as_index=False)
    .agg(valor=('valor_total', 'sum'))
)


fig_secretaria = px.line(
    total_anual_secretaria,
    x=coluna_geral,
    y="valor",
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

fig_secretaria = px.bar(
    total_por_secretaria,
    x='secretaria',
    y='valor',
    text_auto='.2s',
    title='Total Geral por Secretaria',
    subtitle=f"Periodo: {ano_min} - {ano_max}",
)

fig_secretaria.update_layout(
    xaxis_title='Secretaria',
    yaxis_title=titulo_y,
)



fig_pizza = px.pie(
    total_por_secretaria,
    values='valor',
    names='secretaria',
    title='Total Geral por Secretaria',
    subtitle=f"Periodo: {ano_min} - {ano_max}",
)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_secretaria, width='stretch')
with col2:
    st.plotly_chart(fig_pizza, width='stretch')












# -------------------------------------------------
# Valor por Litro
# -------------------------------------------------
fig_litro = px.scatter(
    df,
    x='data_hora',
    y='valor_unitario',
    color='combustivel_tipo',
    title='Valor do combustivel por Requisição',
)

fig_litro.update_layout(
    xaxis_title='Data Hora',
    yaxis_title='Valor por Litro (R$)'
)

st.plotly_chart(fig_litro, width="stretch")











# -------------------------------------------------
# Veículos por ano
# -------------------------------------------------
frota_evolucao = (
    df
    .groupby('ano', as_index=False)
    .agg(
        qtde_veiculos=('codigo_veiculo', 'nunique')
    )
)

# -------------------------------------------------
# Veículos por ano E tipo de combustível
# -------------------------------------------------
agrupar_flex = st.segmented_control(
    "Agrupar Flex e Gasolina",
    options=["Separar", "Agrupar"],
    default="Separar",
)

frota_evolucao_tipo = (
    df
    .groupby(['ano', 'combustivel'], as_index=False)
    .agg(
        qtde_veiculos=('codigo_veiculo', 'nunique')
    )
)

if agrupar_flex == "Agrupar":
    frota_evolucao_tipo['combustivel'] = frota_evolucao_tipo['combustivel'].replace(
        {
            "06 - Flex e semelhantes": "FLEX AGRUPADA",
            "02 - Gasolina": "FLEX AGRUPADA",
        }
    )
    
    frota_evolucao_tipo = (
        frota_evolucao_tipo
        .groupby(['ano', 'combustivel'], as_index=False)
        .agg(
            qtde_veiculos=('qtde_veiculos', 'sum')
        )
    )

# -------------------------------------------------
# Criar gráfico único combinado
# -------------------------------------------------
fig_combinado = go.Figure()

# Adicionar linha do total
fig_combinado.add_trace(
    go.Scatter(
        x=frota_evolucao['ano'],
        y=frota_evolucao['qtde_veiculos'],
        mode='lines+markers',
        name='Total',
        line=dict(width=3),
        marker=dict(size=10)
    )
)

# Adicionar linhas por tipo de combustível
for combustivel in frota_evolucao_tipo['combustivel'].unique():
    dados_combustivel = frota_evolucao_tipo[frota_evolucao_tipo['combustivel'] == combustivel]
    fig_combinado.add_trace(
        go.Scatter(
            x=dados_combustivel['ano'],
            y=dados_combustivel['qtde_veiculos'],
            mode='lines+markers',
            name=combustivel,
            line=dict(width=2),
            marker=dict(size=8)
        )
    )

# Atualizar layout
fig_combinado.update_layout(
    title='Evolução da Frota de Veículos<br><sup>veículos únicos abastecidos durante o ano</sup>',
    xaxis_title='Ano',
    yaxis_title='Quantidade de Veículos',
    height=500,
    showlegend=True,
    hovermode='x unified',
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02
    )
)

st.plotly_chart(fig_combinado, width='stretch')

st.info("Veiculos únicos abastecidos durante o ano. Se um veículo foi abastecido em mais de um ano, ele será contado em cada ano correspondente.")


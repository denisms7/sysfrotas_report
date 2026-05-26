import streamlit as st


st.logo('img/logopm.png', size="large")

pages = {
    "Monitoramento": [
        st.Page("pages/Alertas.py", title="Alertas de Consumo", icon="🔔"),
        st.Page("pages/Alertas_Centros.py", title="Alertas por Centro de Custo", icon="🏢"),
        st.Page("pages/Capacidade_Tanque.py", title="Capacidade do Tanque", icon="⛽"),
    ],
    "Requisicoes": [
        st.Page("pages/Geral.py", title="Combustivel Utilizado", icon="📊"),
        st.Page("pages/Requisicao.py", title="Litros por Requisicoes", icon="🔍"),
        st.Page("pages/Veiculos.py", title="Veiculos Individuais", icon="🚗"),
    ],
}

pg = st.navigation(pages)
pg.run()

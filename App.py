import streamlit as st


st.logo('img/logopm.png', size="large")

pages = {
    "🚨 Monitoramento": [
        st.Page("pages/Alertas.py", title="Alertas de Consumo"),
        st.Page("pages/Alertas_Centros.py", title="Alertas por Centro de Custo"),
    ],
    "📄 Requisicoes": [
        st.Page("pages/Geral.py", title="Combustivel Utilizado"),
        st.Page("pages/Requisicao.py", title="Litros por Requisicoes"),
        st.Page("pages/Veiculos.py", title="Veiculos Individuais"),
    ],
}

pg = st.navigation(pages)
pg.run()

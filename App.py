import streamlit as st


st.logo('img/logopm.png', size="large")

pages = {
    "Requisições de Abastecimentos": [
        st.Page("pages/Geral.py", title="Combustível Utilizado"),
        st.Page("pages/Requisicao.py", title="Litros por Requisições"),
        st.Page("pages/Veiculos.py", title="Veiculos"),
        st.Page("pages/Centros_de_Custo.py", title="Centros de Custo"),
    ],
}

pg = st.navigation(pages)
pg.run()

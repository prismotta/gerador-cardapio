import streamlit as st


def render_sidebar():

    st.sidebar.header("Configurações")

    morador = st.sidebar.selectbox(
        "Selecionar morador",
        ["Morador 1 (Massa)", "Morador 2 (Emagrecer)"]
    )

    # =========================
    # CONFIG POR MORADOR
    # =========================

    if morador == "Morador 1 (Massa)":
        config_local = st.session_state.config_m1
    else:
        config_local = st.session_state.config_m2

    config_local["modo_economico"] = st.sidebar.checkbox(
        "Modo econômico",
        value=config_local["modo_economico"]
    )

    config_local["ovos_refeicao"] = st.sidebar.slider(
        "Quantidade de ovos por refeição",
        1, 6,
        config_local["ovos_refeicao"]
    )

    # =========================
    # META DE CONSUMO (POR MORADOR)
    # =========================

    chave_meta = f"meta_{morador}"

    if chave_meta not in st.session_state:
        if morador == "Morador 1 (Massa)":
            st.session_state[chave_meta] = 2000
        else:
            st.session_state[chave_meta] = 1400

    meta_diaria = st.sidebar.number_input(
        "Meta de consumo diário (g)",
        min_value=500,
        max_value=5000,
        step=100,
        value=st.session_state[chave_meta]
    )

    st.session_state[chave_meta] = meta_diaria

    # =========================
    # RAP10
    # =========================

    limite_rap10 = st.sidebar.slider(
        "Limite de Rap10 por semana",
        0, 7,
        st.session_state.get("limite_rap10", 2)
    )

    st.session_state["limite_rap10"] = limite_rap10

    mostrar_resumo = st.sidebar.checkbox("Mostrar lista de compras")

    return morador, config_local, limite_rap10, mostrar_resumo, meta_diaria
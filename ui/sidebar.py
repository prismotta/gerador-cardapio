import streamlit as st


def render_sidebar(moradores):

    st.sidebar.header("Configurações")

    # =====================================================
    # SELEÇÃO DINÂMICA DE MORADOR
    # =====================================================

    nomes_moradores = [m[1] for m in moradores]

    morador_nome = st.sidebar.selectbox(
        "Selecionar morador",
        nomes_moradores
    )

    morador_data = next(m for m in moradores if m[1] == morador_nome)
    morador_id = morador_data[0]
    meta_diaria = morador_data[2]

    # =====================================================
    # CONFIG LOCAL POR MORADOR
    # =====================================================

    chave_config = f"config_{morador_id}"

    if chave_config not in st.session_state:
        st.session_state[chave_config] = {
            "modo_economico": False,
            "ovos_refeicao": 3
        }

    config_local = st.session_state[chave_config]

    config_local["modo_economico"] = st.sidebar.checkbox(
        "Modo econômico",
        value=config_local["modo_economico"]
    )

    config_local["ovos_refeicao"] = st.sidebar.slider(
        "Quantidade de ovos por refeição",
        1, 6,
        config_local["ovos_refeicao"]
    )

    # =====================================================
    # RAP10
    # =====================================================

    limite_rap10 = st.sidebar.slider(
        "Limite de Rap10 por semana",
        0, 7,
        st.session_state.get("limite_rap10", 2)
    )

    st.session_state["limite_rap10"] = limite_rap10

    mostrar_resumo = st.sidebar.checkbox("Mostrar lista de compras")

    return morador_id, morador_nome, config_local, limite_rap10, mostrar_resumo, meta_diaria
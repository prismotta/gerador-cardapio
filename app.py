"""
app.py
-------------------------------------------------------
Arquivo principal da aplicação.

Responsável por:
- Inicializar banco
- Controlar login
- Garantir onboarding de alimentos
- Controlar modo administrador
- Gerar cardápio
- Exibir listas e métricas

Este arquivo NÃO contém regra de negócio.
Ele apenas orquestra os módulos.
-------------------------------------------------------
"""

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st

from database.db import (
    criar_tabelas,
    carregar_alimentos_dict,
    garantir_alimentos_iniciais
)

from ui.login import tela_login
from ui.painel_alimentos import painel_alimentos

from core.gerador import gerar_cardapio
from ui.sidebar import render_sidebar
from ui.botoes import render_botoes
from ui.visualizacao import (
    mostrar_cardapio,
    mostrar_lista_individual,
    mostrar_lista_familia
)

# =========================================================
# INICIALIZAÇÃO BANCO
# =========================================================

criar_tabelas()

# =========================================================
# CONFIGURAÇÃO STREAMLIT
# =========================================================

st.set_page_config(
    page_title="Gerador de Cardápio",
    layout="wide"
)

# =========================================================
# CONTROLE DE LOGIN
# =========================================================

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    tela_login()
    st.stop()

# Garantir que usuario_id seja inteiro
usuario_id = st.session_state.get("usuario_id")

if isinstance(usuario_id, tuple):
    usuario_id = usuario_id[0]
    st.session_state.usuario_id = usuario_id

if not usuario_id:
    st.error("Erro ao identificar usuário.")
    st.stop()

# =========================================================
# ONBOARDING AUTOMÁTICO
# =========================================================

garantir_alimentos_iniciais(usuario_id)

# =========================================================
# INTERFACE PRINCIPAL
# =========================================================

st.title("Gerador de Cardápio")

col1, col2 = st.columns([1, 3])

with col1:
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

with col2:
    modo_admin = st.toggle("Modo administrador")

# =========================================================
# PAINEL ADMIN
# =========================================================

if modo_admin:
    painel_alimentos(usuario_id)
    st.stop()

# =========================================================
# ESTADO INICIAL
# =========================================================

if "config_m1" not in st.session_state:
    st.session_state.config_m1 = {
        "modo_economico": False,
        "ovos_refeicao": 3
    }

if "config_m2" not in st.session_state:
    st.session_state.config_m2 = {
        "modo_economico": False,
        "ovos_refeicao": 2
    }

if "semana_m1" not in st.session_state:
    st.session_state.semana_m1 = None

if "semana_m2" not in st.session_state:
    st.session_state.semana_m2 = None

# =========================================================
# SIDEBAR CONFIGURAÇÃO
# =========================================================

morador, config_local, limite_rap10, mostrar_resumo, meta_diaria = render_sidebar()

# =========================================================
# FUNÇÃO GERADORA
# =========================================================

def gerar_semana():
    """
    Busca alimentos atualizados do banco
    e gera cardápio.
    """

    alimentos = carregar_alimentos_dict(usuario_id)

    if not alimentos:
        st.warning("Nenhum alimento cadastrado.")
        return None

    return gerar_cardapio(
        morador,
        config_local,
        limite_rap10,
        alimentos
    )

# =========================================================
# INICIALIZAÇÃO SEMANA
# =========================================================

if morador == "Morador 1 (Massa)":

    if st.session_state.semana_m1 is None:
        st.session_state.semana_m1 = gerar_semana()

    semana_ativa = st.session_state.semana_m1

else:

    if st.session_state.semana_m2 is None:
        st.session_state.semana_m2 = gerar_semana()

    semana_ativa = st.session_state.semana_m2

# =========================================================
# REGERAÇÃO AUTOMÁTICA
# =========================================================

chave_config = f"config_anterior_{morador}"

config_atual = {
    "modo_economico": config_local["modo_economico"],
    "ovos_refeicao": config_local["ovos_refeicao"],
    "limite_rap10": limite_rap10
}

if chave_config not in st.session_state:
    st.session_state[chave_config] = config_atual

if st.session_state[chave_config] != config_atual:

    st.session_state[chave_config] = config_atual

    nova_semana = gerar_semana()

    if morador == "Morador 1 (Massa)":
        st.session_state.semana_m1 = nova_semana
        semana_ativa = nova_semana
    else:
        st.session_state.semana_m2 = nova_semana
        semana_ativa = nova_semana

# =========================================================
# BOTÕES
# =========================================================

acao = render_botoes()

if acao == "nova":

    nova_semana = gerar_semana()

    if morador == "Morador 1 (Massa)":
        st.session_state.semana_m1 = nova_semana
        semana_ativa = nova_semana
    else:
        st.session_state.semana_m2 = nova_semana
        semana_ativa = nova_semana

# =========================================================
# EXIBIÇÃO
# =========================================================

if semana_ativa:

    mostrar_cardapio(semana_ativa, morador, meta_diaria)

    if mostrar_resumo:
        mostrar_lista_individual(semana_ativa, morador)

    with st.expander("Lista unificada (Morador 1 + Morador 2)"):

        if st.session_state.semana_m1 and st.session_state.semana_m2:

            mostrar_lista_familia(
                st.session_state.semana_m1,
                st.session_state.semana_m2
            )
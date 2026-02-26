"""
app.py
-------------------------------------------------------
Arquivo principal da aplicação.

Compatível com nova modelagem:
- usuarios
- moradores
- alimentos
- porcoes

Sem duplicação.
-------------------------------------------------------
"""

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st

from database.db import (
    criar_tabelas,
    get_connection,
    get_placeholder
)

from core.gerador import (
    gerar_cardapio,
    regenerar_almoco,
    regenerar_lanche,
    regenerar_jantar
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

usuario = st.session_state.get("usuario_id")

if not usuario:
    st.error("Usuário não autenticado.")
    st.stop()

if isinstance(usuario, tuple):
    usuario_id = usuario[0]
else:
    usuario_id = usuario

usuario_id = int(usuario_id)
st.session_state.usuario_id = usuario_id

# =========================================================
# BUSCAR MORADORES DINAMICAMENTE
# =========================================================

def listar_moradores(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()

    cursor.execute(
        f"""
        SELECT id, nome, meta_calorica
        FROM moradores
        WHERE usuario_id = {placeholder}
        """,
        (usuario_id,)
    )

    dados = cursor.fetchall()
    conn.close()
    return dados


moradores = listar_moradores(usuario_id)

if not moradores:
    st.error("Nenhum morador cadastrado.")
    st.stop()

# =========================================================
# INTERFACE
# =========================================================

st.title("Gerador de Cardápio")

col1, col2 = st.columns([1, 3])

with col1:
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

with col2:
    modo_admin = st.toggle("Modo administrador")

if modo_admin:
    painel_alimentos(usuario_id)
    st.stop()

# =========================================================
# SELEÇÃO DINÂMICA DE MORADOR
# =========================================================

nomes_moradores = [m[1] for m in moradores]
morador_nome = st.selectbox("Selecionar morador", nomes_moradores)

morador_data = next(m for m in moradores if m[1] == morador_nome)
morador_id = morador_data[0]
meta_diaria = morador_data[2]

# =========================================================
# CARREGAR ALIMENTOS DO USUÁRIO
# =========================================================

def carregar_alimentos(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()

    cursor.execute(
        f"""
        SELECT id, nome, preco
        FROM alimentos
        WHERE usuario_id = {placeholder}
        """,
        (usuario_id,)
    )

    dados = cursor.fetchall()
    conn.close()

    return dados


alimentos = carregar_alimentos(usuario_id)

if not alimentos:
    st.warning("Nenhum alimento cadastrado.")
    st.stop()

# =========================================================
# GERAÇÃO
# =========================================================

if "semana" not in st.session_state:
    st.session_state.semana = None


def gerar_semana():
    return gerar_cardapio(
        morador_id,
        alimentos
    )


if st.session_state.semana is None:
    st.session_state.semana = gerar_semana()

acao = render_botoes()

if acao == "nova":
    st.session_state.semana = gerar_semana()

elif acao == "almoco":
    st.session_state.semana = regenerar_almoco(
        st.session_state.semana,
        dia_index,
        alimentos
    )

elif acao == "lanche":
    st.session_state.semana = regenerar_lanche(
        st.session_state.semana,
        dia_index
    )

elif acao == "jantar":
    st.session_state.semana = regenerar_jantar(
        st.session_state.semana,
        dia_index,
        alimentos
    )

# =========================================================
# EXIBIÇÃO
# =========================================================

if st.session_state.semana:
    mostrar_cardapio(st.session_state.semana, morador_nome, meta_diaria)
    mostrar_lista_individual(st.session_state.semana, morador_nome)
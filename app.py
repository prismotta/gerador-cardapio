"""
app.py
-------------------------------------------------------
Arquivo principal da aplicação.
-------------------------------------------------------
"""

import streamlit as st

from database.db import criar_tabelas, get_connection, get_placeholder
from core.gerador import (
    gerar_cardapio,
    regenerar_almoco,
    regenerar_lanche,
    regenerar_jantar,
)
from ui.login import tela_login
from ui.painel_alimentos import painel_alimentos
from ui.botoes import render_botoes
from ui.visualizacao import mostrar_cardapio, mostrar_lista_individual


criar_tabelas()

st.set_page_config(page_title="Gerador de Cardápio", layout="wide")

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
        (usuario_id,),
    )

    dados = cursor.fetchall()
    conn.close()
    return dados


moradores = listar_moradores(usuario_id)

if not moradores:
    from database.db import onboarding_inicial

    onboarding_inicial(usuario_id)
    moradores = listar_moradores(usuario_id)

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

nomes_moradores = [m[1] for m in moradores]
morador_nome = st.selectbox("Selecionar morador", nomes_moradores)

morador_data = next(m for m in moradores if m[1] == morador_nome)
morador_id = morador_data[0]
meta_padrao = int(morador_data[2])

meta_key = f"meta_diaria_{morador_id}"
if meta_key not in st.session_state:
    st.session_state[meta_key] = meta_padrao

meta_diaria = st.number_input(
    "Meta diária (g)",
    min_value=0,
    step=50,
    key=meta_key,
)


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
        (usuario_id,),
    )
    dados = cursor.fetchall()

    cursor.execute(
        f"""
        SELECT pa.alimento_id, pa.nome
        FROM preparos_alimento pa
        JOIN alimentos a ON a.id = pa.alimento_id
        WHERE a.usuario_id = {placeholder}
        ORDER BY pa.nome
        """,
        (usuario_id,),
    )
    preparos_raw = cursor.fetchall()
    conn.close()

    preparos_por_alimento = {}
    for alimento_id, preparo_nome in preparos_raw:
        preparos_por_alimento.setdefault(alimento_id, []).append(preparo_nome)

    alimentos = []
    for alimento_id, nome, preco in dados:
        alimentos.append(
            {
                "id": alimento_id,
                "nome": nome,
                "preco": preco,
                "preparos": preparos_por_alimento.get(alimento_id, []),
            }
        )

    return alimentos


alimentos = carregar_alimentos(usuario_id)
if not alimentos:
    st.warning("Nenhum alimento cadastrado.")
    st.stop()

if "semana" not in st.session_state:
    st.session_state.semana = None


def gerar_semana():
    return gerar_cardapio(morador_id, alimentos)


if st.session_state.semana is None:
    st.session_state.semana = gerar_semana()

dia_opcoes = [d["Dia"] for d in st.session_state.semana]

if "dia_para_troca" not in st.session_state:
    st.session_state.dia_para_troca = dia_opcoes[0]
elif st.session_state.dia_para_troca not in dia_opcoes:
    st.session_state.dia_para_troca = dia_opcoes[0]

dia_selecionado = st.selectbox("Dia para trocar refeição", dia_opcoes, key="dia_para_troca")
dia_index = dia_opcoes.index(dia_selecionado)

acao = render_botoes()

if acao == "nova":
    st.session_state.semana = gerar_semana()
elif acao == "almoco":
    st.session_state.semana = regenerar_almoco(st.session_state.semana, dia_index, alimentos)
elif acao == "lanche":
    st.session_state.semana = regenerar_lanche(st.session_state.semana, dia_index)
elif acao == "jantar":
    st.session_state.semana = regenerar_jantar(st.session_state.semana, dia_index, alimentos)

if st.session_state.semana:
    mostrar_cardapio(st.session_state.semana, morador_nome, meta_diaria)
    mostrar_lista_individual(st.session_state.semana, morador_nome)

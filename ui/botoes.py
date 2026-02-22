import streamlit as st


def render_botoes():

    col1, col2, col3, col4 = st.columns(4)

    acao = None

    if col1.button("Gerar nova semana"):
        acao = "nova"

    if col2.button("Trocar apenas almoço"):
        acao = "almoco"

    if col3.button("Trocar apenas lanche"):
        acao = "lanche"

    if col4.button("Trocar apenas jantar"):
        acao = "jantar"

    return acao
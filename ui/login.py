import streamlit as st
from database.db import criar_usuario, autenticar_usuario


def tela_login():

    st.title("🔐 Acesso ao Sistema")
    st.markdown("---")

    aba = st.radio("Escolha uma opção:", ["Entrar", "Cadastrar"], horizontal=True)

    username = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    # Normalização
    username = username.strip().lower()

    # =====================================================
    # LOGIN
    # =====================================================

    if aba == "Entrar":

        if st.button("Entrar", use_container_width=True):

            if not username or not senha:
                st.warning("Preencha usuário e senha.")
                return

            usuario = autenticar_usuario(username, senha)

            if usuario:
                usuario_id = usuario[0]

                st.session_state.usuario_id = usuario_id
                st.session_state.username = usuario[1]
                st.session_state.logado = True

                st.success("Login realizado com sucesso!")
                st.rerun()

            else:
                st.error("Usuário ou senha incorretos.")

    # =====================================================
    # CADASTRO
    # =====================================================

    else:

        if st.button("Cadastrar", use_container_width=True):

            if not username or not senha:
                st.warning("Preencha usuário e senha.")
                return

            if len(senha) < 4:
                st.warning("A senha deve ter pelo menos 4 caracteres.")
                return

            sucesso = criar_usuario(username, senha)

            if sucesso:
                st.success("Usuário criado com sucesso! Agora faça login.")
            else:
                st.error("Usuário já existe ou erro no cadastro.")
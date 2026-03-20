import streamlit as st
from database.db import criar_usuario, autenticar_usuario
from database.sessao import salvar_sessao, limpar_sessao


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
        manter_logado = st.checkbox("Manter logado", value=False)

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

                # Salvar sessão se marcado "Manter logado"
                if manter_logado:
                    salvar_sessao(usuario_id, usuario[1])
                else:
                    limpar_sessao()

                st.toast("Login realizado com sucesso! 🎉")
                st.rerun()

            else:
                st.error("Usuário ou senha incorretos.")
                limpar_sessao()

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
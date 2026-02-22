"""
ui/painel_alimentos.py
-------------------------------------------------------
Painel administrativo para gerenciamento de alimentos.

Permite:
- Listar alimentos do usuário
- Editar nome, gramas e preço
- Excluir alimento
- Adicionar novo alimento

Fluxo:
UI → db.py → Banco

Apenas usuários autenticados podem acessar.
-------------------------------------------------------
"""

import streamlit as st
from database.db import (
    listar_alimentos_usuario,
    atualizar_alimento,
    deletar_alimento,
    inserir_alimento,
)


def painel_alimentos(usuario_id):
    """
    Renderiza painel de gerenciamento de alimentos.
    """

    st.subheader("🛠 Gerenciar Alimentos")
    st.markdown("---")

    alimentos = listar_alimentos_usuario(usuario_id)

    # =====================================================
    # LISTA DE ALIMENTOS EXISTENTES
    # =====================================================

    if not alimentos:
        st.info("Nenhum alimento cadastrado ainda.")

    for chave, nome, gramas, preco in alimentos:

        with st.expander(f"{nome} ({chave})", expanded=False):

            novo_nome = st.text_input(
                "Nome do alimento",
                value=nome,
                key=f"nome_{chave}"
            )

            novo_gramas = st.number_input(
                "Gramas por refeição",
                min_value=1,
                value=int(gramas),
                key=f"g_{chave}"
            )

            novo_preco = st.number_input(
                "Preço por kg",
                min_value=0.0,
                value=float(preco),
                key=f"p_{chave}"
            )

            col1, col2 = st.columns(2)

            # =================================================
            # SALVAR ALTERAÇÕES
            # =================================================

            if col1.button("💾 Salvar", key=f"save_{chave}"):

                if not novo_nome.strip():
                    st.error("O nome não pode estar vazio.")
                    return

                atualizar_alimento(
                    usuario_id,
                    chave,
                    novo_nome.strip(),
                    int(novo_gramas),
                    float(novo_preco),
                )

                st.success("Alimento atualizado com sucesso!")
                st.rerun()

            # =================================================
            # EXCLUIR (COM CONFIRMAÇÃO)
            # =================================================

            if col2.button("🗑 Excluir", key=f"del_{chave}"):

                confirmar = st.checkbox(
                    "Confirmar exclusão",
                    key=f"confirm_{chave}"
                )

                if confirmar:
                    deletar_alimento(usuario_id, chave)
                    st.warning("Alimento removido.")
                    st.rerun()

    # =====================================================
    # ADICIONAR NOVO ALIMENTO
    # =====================================================

    st.divider()
    st.subheader("➕ Adicionar Novo Alimento")

    nova_chave = st.text_input("Chave interna (ex: Arroz_M1)")
    novo_nome = st.text_input("Nome do alimento")
    novo_gramas = st.number_input("Gramas por refeição", min_value=1, step=10)
    novo_preco = st.number_input("Preço por kg", min_value=0.0, step=0.5)

    if st.button("Adicionar alimento", use_container_width=True):

        nova_chave = nova_chave.strip()
        novo_nome = novo_nome.strip()

        if not nova_chave or not novo_nome:
            st.error("Preencha chave e nome.")
            return

        # 🔒 Evitar chave duplicada
        chaves_existentes = [a[0] for a in alimentos]

        if nova_chave in chaves_existentes:
            st.error("Essa chave já existe.")
            return

        inserir_alimento(
            usuario_id,
            nova_chave,
            novo_nome,
            int(novo_gramas),
            float(novo_preco),
        )

        st.success("Alimento adicionado com sucesso!")
        st.rerun()
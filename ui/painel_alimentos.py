"""
ui/painel_alimentos.py
-------------------------------------------------------
Painel administrativo compatível com nova modelagem:

- alimentos (nome + preco)
- moradores
- porcoes (gramas por morador)
-------------------------------------------------------
"""

import streamlit as st
from database.db import (
    get_connection,
    get_placeholder,
)


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def listar_alimentos(usuario_id):
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


# =========================================================
# PAINEL
# =========================================================

def painel_alimentos(usuario_id):

    st.subheader("🛠 Painel Administrativo")
    st.markdown("---")

    # =====================================================
    # ALIMENTOS
    # =====================================================

    st.subheader("🍗 Alimentos")

    alimentos = listar_alimentos(usuario_id)

    for alimento_id, nome, preco in alimentos:

        with st.expander(f"{nome}"):

            novo_nome = st.text_input(
                "Nome",
                value=nome,
                key=f"nome_{alimento_id}"
            )

            novo_preco = st.number_input(
                "Preço por kg",
                min_value=0.0,
                value=float(preco),
                key=f"preco_{alimento_id}"
            )

            if st.button("Salvar", key=f"save_al_{alimento_id}"):

                conn = get_connection()
                cursor = conn.cursor()
                placeholder = get_placeholder()

                cursor.execute(
                    f"""
                    UPDATE alimentos
                    SET nome = {placeholder},
                        preco = {placeholder}
                    WHERE id = {placeholder}
                    """,
                    (novo_nome.strip(), float(novo_preco), alimento_id)
                )

                conn.commit()
                conn.close()

                st.success("Atualizado!")
                st.rerun()

    # =====================================================
    # MORADORES
    # =====================================================

    st.divider()
    st.subheader("👤 Moradores")

    moradores = listar_moradores(usuario_id)

    for morador_id, nome, meta in moradores:

        with st.expander(f"{nome}"):

            novo_nome = st.text_input(
                "Nome",
                value=nome,
                key=f"mor_nome_{morador_id}"
            )

            nova_meta = st.number_input(
                "Meta calórica",
                min_value=0,
                value=int(meta),
                key=f"meta_{morador_id}"
            )

            if st.button("Salvar", key=f"save_mor_{morador_id}"):

                conn = get_connection()
                cursor = conn.cursor()
                placeholder = get_placeholder()

                cursor.execute(
                    f"""
                    UPDATE moradores
                    SET nome = {placeholder},
                        meta_calorica = {placeholder}
                    WHERE id = {placeholder}
                    """,
                    (novo_nome.strip(), int(nova_meta), morador_id)
                )

                conn.commit()
                conn.close()

                st.success("Morador atualizado!")
                st.rerun()

    st.info("⚙ Porções por morador serão integradas na próxima melhoria.")
"""
ui/painel_alimentos.py
-------------------------------------------------------
Painel administrativo:
- alimentos (nome + preco)
- moradores (nome + meta calorica)
-------------------------------------------------------
"""

import streamlit as st
from database.db import get_connection, get_placeholder


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
        (usuario_id,),
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
        (usuario_id,),
    )
    dados = cursor.fetchall()
    conn.close()
    return dados


def listar_preparos_alimento(alimento_id):
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()
    cursor.execute(
        f"""
        SELECT id, nome
        FROM preparos_alimento
        WHERE alimento_id = {placeholder}
        ORDER BY nome
        """,
        (alimento_id,),
    )
    dados = cursor.fetchall()
    conn.close()
    return dados


def painel_alimentos(usuario_id):
    st.subheader("Painel Administrativo")
    st.markdown("---")

    st.subheader("Alimentos")
    alimentos = listar_alimentos(usuario_id)

    with st.expander("Adicionar alimento"):
        nome_alimento_novo = st.text_input("Nome do novo alimento", key="add_al_nome")
        preco_alimento_novo = st.number_input(
            "Preco por kg do novo alimento",
            min_value=0.0,
            value=0.0,
            key="add_al_preco",
        )

        if st.button("Adicionar alimento", key="add_al_btn"):
            nome_limpo = nome_alimento_novo.strip()
            if not nome_limpo:
                st.warning("Informe um nome.")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                placeholder = get_placeholder()
                try:
                    cursor.execute(
                        f"""
                        INSERT INTO alimentos (usuario_id, nome, preco)
                        VALUES ({placeholder}, {placeholder}, {placeholder})
                        """,
                        (usuario_id, nome_limpo, float(preco_alimento_novo)),
                    )
                    conn.commit()
                    st.success("Alimento adicionado.")
                    st.rerun()
                except Exception:
                    st.error("Nao foi possivel adicionar. Nome pode ja existir.")
                finally:
                    conn.close()

    for alimento_id, nome, preco in alimentos:
        with st.expander(nome):
            novo_nome = st.text_input("Nome", value=nome, key=f"nome_{alimento_id}")
            novo_preco = st.number_input(
                "Preco por kg",
                min_value=0.0,
                value=float(preco),
                key=f"preco_{alimento_id}",
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
                    (novo_nome.strip(), float(novo_preco), alimento_id),
                )
                conn.commit()
                conn.close()
                st.success("Alimento atualizado.")
                st.rerun()

            if st.button("Remover alimento", key=f"del_al_{alimento_id}"):
                conn = get_connection()
                cursor = conn.cursor()
                placeholder = get_placeholder()
                try:
                    cursor.execute(
                        f"DELETE FROM porcoes WHERE alimento_id = {placeholder}",
                        (alimento_id,),
                    )
                    cursor.execute(
                        f"DELETE FROM alimentos WHERE id = {placeholder}",
                        (alimento_id,),
                    )
                    conn.commit()
                    st.success("Alimento removido.")
                    st.rerun()
                except Exception:
                    st.error("Nao foi possivel remover o alimento.")
                finally:
                    conn.close()

            st.markdown("**Modos de preparo**")
            preparos = listar_preparos_alimento(alimento_id)
            for preparo_id, preparo_nome in preparos:
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.text(preparo_nome)
                with c2:
                    if st.button("Remover", key=f"del_prep_{preparo_id}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        placeholder = get_placeholder()
                        cursor.execute(
                            f"DELETE FROM preparos_alimento WHERE id = {placeholder}",
                            (preparo_id,),
                        )
                        conn.commit()
                        conn.close()
                        st.rerun()

            novo_preparo = st.text_input("Novo preparo", key=f"novo_prep_{alimento_id}")
            if st.button("Adicionar preparo", key=f"add_prep_{alimento_id}"):
                preparo_limpo = novo_preparo.strip()
                if not preparo_limpo:
                    st.warning("Informe um preparo.")
                else:
                    conn = get_connection()
                    cursor = conn.cursor()
                    placeholder = get_placeholder()
                    try:
                        cursor.execute(
                            f"""
                            INSERT INTO preparos_alimento (alimento_id, nome)
                            VALUES ({placeholder}, {placeholder})
                            """,
                            (alimento_id, preparo_limpo),
                        )
                        conn.commit()
                        st.success("Preparo adicionado.")
                        st.rerun()
                    except Exception:
                        st.error("Nao foi possivel adicionar. Esse preparo pode ja existir.")
                    finally:
                        conn.close()

    st.divider()
    st.subheader("Moradores")
    moradores = listar_moradores(usuario_id)

    with st.expander("Adicionar morador"):
        nome_novo = st.text_input("Nome do novo morador", key="add_morador_nome")
        meta_nova = st.number_input(
            "Meta calorica do novo morador",
            min_value=0,
            value=2000,
            key="add_morador_meta",
        )

        if st.button("Adicionar morador", key="add_morador_btn"):
            nome_limpo = nome_novo.strip()
            if not nome_limpo:
                st.warning("Informe um nome.")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                placeholder = get_placeholder()
                try:
                    cursor.execute(
                        f"""
                        INSERT INTO moradores (usuario_id, nome, meta_calorica)
                        VALUES ({placeholder}, {placeholder}, {placeholder})
                        """,
                        (usuario_id, nome_limpo, int(meta_nova)),
                    )
                    conn.commit()
                    st.success("Morador adicionado.")
                    st.rerun()
                except Exception:
                    st.error("Nao foi possivel adicionar. Nome pode ja existir.")
                finally:
                    conn.close()

    for morador_id, nome, meta in moradores:
        with st.expander(nome):
            novo_nome = st.text_input("Nome", value=nome, key=f"mor_nome_{morador_id}")
            nova_meta = st.number_input(
                "Meta calorica",
                min_value=0,
                value=int(meta),
                key=f"meta_{morador_id}",
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
                    (novo_nome.strip(), int(nova_meta), morador_id),
                )
                conn.commit()
                conn.close()
                st.success("Morador atualizado.")
                st.rerun()

            pode_remover = len(moradores) > 1
            if st.button(
                "Remover morador",
                key=f"del_mor_{morador_id}",
                disabled=not pode_remover,
            ):
                conn = get_connection()
                cursor = conn.cursor()
                placeholder = get_placeholder()
                try:
                    cursor.execute(
                        f"DELETE FROM porcoes WHERE morador_id = {placeholder}",
                        (morador_id,),
                    )
                    cursor.execute(
                        f"DELETE FROM moradores WHERE id = {placeholder}",
                        (morador_id,),
                    )
                    conn.commit()
                    st.success("Morador removido.")
                    st.rerun()
                except Exception:
                    st.error("Nao foi possivel remover o morador.")
                finally:
                    conn.close()

            if not pode_remover:
                st.caption("Pelo menos um morador deve permanecer.")

    st.info("Porcoes por morador serao integradas em uma proxima melhoria.")

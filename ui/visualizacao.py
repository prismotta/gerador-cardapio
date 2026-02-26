"""
ui/visualizacao.py
-------------------------------------------------------
Responsável pela exibição do cardápio e listas de compra.

Compatível com nova modelagem:
- alimentos únicos
- moradores dinâmicos
- sem dependência de _M1/_M2

Este módulo:
- NÃO gera dados
- NÃO acessa banco
- Apenas exibe informações formatadas
-------------------------------------------------------
"""

import streamlit as st
import pandas as pd
from export.pdf_export import gerar_pdf_lista
from export.image_export import gerar_jpg_lista
from core.compras import calcular_lista_compras


# =========================================================
# AUXILIAR
# =========================================================

def _obter_gramas(item):
    """
    Compatível com:
    - g
    - gramas
    - ausência de peso
    """
    return item.get("g") or item.get("gramas") or 0


# =========================================================
# CARDÁPIO
# =========================================================

def mostrar_cardapio(semana, morador_nome, meta):

    if not semana:
        st.warning("Nenhum cardápio gerado ainda.")
        return None

    dados = []
    totais_semana = []

    for d in semana:

        almoco = d["Almoço"]
        jantar = d["Jantar"]

        total_dia = 0

        for ref in [almoco, jantar]:

            proteina = ref["proteina"]

            # PROTEÍNA
            if isinstance(proteina, dict):
                total_dia += _obter_gramas(proteina)

            # CARBO
            total_dia += _obter_gramas(ref["carbo"])

            # LEGUME
            if "legume" in ref:
                total_dia += _obter_gramas(ref["legume"])

        totais_semana.append(total_dia)

        # Exibição peso
        if total_dia >= 1000:
            peso_exibicao = f"{round(total_dia/1000, 2)} kg"
        else:
            peso_exibicao = f"{total_dia} g"

        diferenca = total_dia - meta

        if diferenca > 0:
            status = f"🟢 +{diferenca} g (Superávit)"
        elif diferenca < 0:
            status = f"🔴 {diferenca} g (Déficit)"
        else:
            status = "⚖️ Meta exata"

        dados.append({
            "Dia": d["Dia"],
            "Almoço": almoco["proteina_formatada"] + " + " + almoco["carbo_formatado"],
            "Lanche": d["Lanche"]["nome"],
            "Jantar": jantar["proteina_formatada"] + " + " + jantar["carbo_formatado"],
            "Peso total": peso_exibicao,
            "Balanço": status
        })

    df = pd.DataFrame(dados)

    st.subheader(f"Cardápio - {morador_nome}")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # MÉDIA SEMANAL
    media = sum(totais_semana) / len(totais_semana)

    if media >= 1000:
        media_exibicao = f"{round(media/1000, 2)} kg"
    else:
        media_exibicao = f"{round(media)} g"

    st.metric("Média diária da semana", media_exibicao)

    return df


# =========================================================
# LISTA INDIVIDUAL
# =========================================================

def mostrar_lista_individual(semana, morador_nome):

    lista_df, custo_total = calcular_lista_compras(semana)

    col_titulo, col_menu = st.columns([8, 1])

    with col_titulo:
        st.subheader(f"Lista de Compras - {morador_nome}")

    with col_menu:
        with st.popover("⭳", use_container_width=True):

            csv = lista_df.to_csv(index=False).encode("utf-8")
            st.download_button("CSV", csv, "lista.csv", use_container_width=True)

            pdf = gerar_pdf_lista(lista_df, f"Lista - {morador_nome}")
            st.download_button("PDF", pdf, "lista.pdf", use_container_width=True)

            jpg = gerar_jpg_lista(lista_df)
            st.download_button("JPG", jpg, "lista.jpg", use_container_width=True)

    st.dataframe(lista_df, use_container_width=True, hide_index=True)
    st.metric("Custo estimado (R$)", custo_total)


# =========================================================
# LISTA FAMÍLIA (DINÂMICA)
# =========================================================

def mostrar_lista_familia(lista_semanas):
    """
    Recebe lista de semanas (qualquer quantidade de moradores).
    """

    listas = []
    custo_total = 0

    for semana in lista_semanas:
        if not semana:
            continue

        lista_df, custo = calcular_lista_compras(semana)
        listas.append(lista_df)
        custo_total += custo

    if not listas:
        st.warning("Nenhuma lista disponível.")
        return

    lista_total = pd.concat(listas)
    lista_total = lista_total.groupby(
        ["Alimento", "Unidade"], as_index=False
    ).agg({
        "Quantidade": "sum",
        "Custo estimado (R$)": "sum"
    })

    col_titulo, col_menu = st.columns([8, 1])

    with col_titulo:
        st.subheader("Lista de Compras - Família")

    with col_menu:
        with st.popover("⭳", use_container_width=True):

            csv = lista_total.to_csv(index=False).encode("utf-8")
            st.download_button("CSV", csv, "familia.csv", use_container_width=True)

            pdf = gerar_pdf_lista(lista_total, "Lista de Compras - Família")
            st.download_button("PDF", pdf, "familia.pdf", use_container_width=True)

            jpg = gerar_jpg_lista(lista_total)
            st.download_button("JPG", jpg, "familia.jpg", use_container_width=True)

    st.dataframe(lista_total, use_container_width=True, hide_index=True)
    st.metric("Custo total família (R$)", round(custo_total, 2))
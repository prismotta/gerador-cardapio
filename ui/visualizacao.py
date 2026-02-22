"""
ui/visualizacao.py
-------------------------------------------------------
Responsável pela exibição do cardápio e listas de compra.

Funções:
- mostrar_cardapio()
- mostrar_lista_individual()
- mostrar_lista_familia()

Este módulo:
- NÃO gera dados
- NÃO acessa banco diretamente
- Apenas exibe informações formatadas
-------------------------------------------------------
"""

import streamlit as st
import pandas as pd
from export.pdf_export import gerar_pdf_lista
from export.image_export import gerar_jpg_lista
from core.compras import calcular_lista_compras


# =========================================================
# CARDÁPIO
# =========================================================

def mostrar_cardapio(semana, morador, meta):
    """
    Exibe tabela do cardápio semanal com:
    - Peso total diário
    - Déficit / Superávit
    - Média semanal
    """

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

            # ================= PROTEÍNA =================

            if isinstance(proteina, dict) and proteina.get("g"):
                total_dia += proteina["g"]

            # ================= CARBO =================

            total_dia += ref["carbo"].get("g", 0)

            # ================= LEGUME =================

            if "legume" in ref:
                total_dia += ref["legume"].get("g", 0)

        totais_semana.append(total_dia)

        # ================= EXIBIÇÃO PESO =================

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

    st.subheader(f"Cardápio - {morador}")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ================= MÉDIA SEMANAL =================

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

def mostrar_lista_individual(semana, morador):
    """
    Exibe lista de compras individual com:
    - Exportação CSV
    - Exportação PDF
    - Exportação JPG
    """

    lista_df, custo_total = calcular_lista_compras(semana)

    col_titulo, col_menu = st.columns([8, 1])

    with col_titulo:
        st.subheader(f"Lista de Compras - {morador}")

    with col_menu:
        with st.popover("⭳", use_container_width=True):

            csv = lista_df.to_csv(index=False).encode("utf-8")
            st.download_button("CSV", csv, "lista.csv", use_container_width=True)

            pdf = gerar_pdf_lista(lista_df, f"Lista - {morador}")
            st.download_button("PDF", pdf, "lista.pdf", use_container_width=True)

            jpg = gerar_jpg_lista(lista_df)
            st.download_button("JPG", jpg, "lista.jpg", use_container_width=True)

    st.dataframe(lista_df, use_container_width=True, hide_index=True)
    st.metric("Custo estimado (R$)", custo_total)


# =========================================================
# LISTA FAMÍLIA
# =========================================================

def mostrar_lista_familia(semana_m1, semana_m2):
    """
    Une lista de dois moradores e consolida valores.
    """

    lista1, custo1 = calcular_lista_compras(semana_m1)
    lista2, custo2 = calcular_lista_compras(semana_m2)

    lista_total = pd.concat([lista1, lista2])
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
    st.metric("Custo total família (R$)", round(custo1 + custo2, 2))
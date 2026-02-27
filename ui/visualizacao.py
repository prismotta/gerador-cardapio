"""
ui/visualizacao.py
-------------------------------------------------------
Exibicao de cardapio e listas de compra.
-------------------------------------------------------
"""

import pandas as pd
import streamlit as st

from core.compras import calcular_lista_compras
from export.image_export import gerar_jpg_lista
from export.pdf_export import gerar_pdf_lista


def _obter_gramas(item):
    gramas = item.get("g") or item.get("gramas")
    if gramas:
        return gramas

    # Fallback para cardapios antigos sem peso no lanche.
    nome = item.get("nome", "")
    if not nome:
        return 0
    if "Banana + Aveia" in nome:
        return 220
    if "Presunto" in nome and "Mussarela" in nome:
        return 180
    if "Pasta de Amendoim" in nome:
        return 230
    if "Vitamina de Banana + Aveia" in nome:
        return 300
    if nome.startswith("Rap10"):
        return 140 if nome.count("+") >= 2 else 100
    return 0


def _refeicao_texto(ref):
    texto = ref["proteina_formatada"] + " + " + ref["carbo_formatado"]
    if "legume" in ref:
        texto += " + " + ref["legume"]["nome"]
    return texto


def mostrar_cardapio(semana, morador_nome, meta):
    if not semana:
        st.warning("Nenhum cardapio gerado ainda.")
        return None

    dados = []
    totais_semana = []
    almoco_key = next((k for k in semana[0].keys() if k.startswith("Almo")), "Almoço")

    for d in semana:
        almoco = d[almoco_key]
        jantar = d["Jantar"]
        total_dia = 0

        for ref in [almoco, jantar]:
            proteina = ref["proteina"]
            if isinstance(proteina, dict):
                total_dia += _obter_gramas(proteina)
            total_dia += _obter_gramas(ref["carbo"])
            if "legume" in ref:
                total_dia += _obter_gramas(ref["legume"])

        total_dia += _obter_gramas(d["Lanche"])
        totais_semana.append(total_dia)

        peso_exibicao = f"{round(total_dia/1000, 2)} kg" if total_dia >= 1000 else f"{total_dia} g"
        diferenca = total_dia - meta

        if diferenca > 0:
            status = f"+{diferenca} g (Superavit)"
        elif diferenca < 0:
            status = f"{diferenca} g (Deficit)"
        else:
            status = "Meta exata"

        lanche_gramas = _obter_gramas(d["Lanche"])
        dados.append(
            {
                "Dia": d["Dia"],
                "Almoço": _refeicao_texto(almoco),
                "Lanche": f"{d['Lanche']['nome']} ({lanche_gramas}g)" if lanche_gramas else d["Lanche"]["nome"],
                "Jantar": _refeicao_texto(jantar),
                "Peso total": peso_exibicao,
                "Balanco": status,
            }
        )

    df = pd.DataFrame(dados)
    st.subheader(f"Cardapio - {morador_nome}")
    st.dataframe(df, use_container_width=True, hide_index=True)

    media = sum(totais_semana) / len(totais_semana)
    media_exibicao = f"{round(media/1000, 2)} kg" if media >= 1000 else f"{round(media)} g"
    st.metric("Media diaria da semana", media_exibicao)
    return df


def mostrar_lista_individual(semana, morador_nome):
    lista_df, custo_total = calcular_lista_compras(semana)

    col_titulo, col_menu = st.columns([8, 1])
    with col_titulo:
        st.subheader(f"Lista de Compras - {morador_nome}")

    with col_menu:
        with st.popover("Exportar", use_container_width=True):
            csv = lista_df.to_csv(index=False).encode("utf-8")
            st.download_button("CSV", csv, "lista.csv", use_container_width=True)

            pdf = gerar_pdf_lista(lista_df, f"Lista - {morador_nome}")
            st.download_button("PDF", pdf, "lista.pdf", use_container_width=True)

            jpg = gerar_jpg_lista(lista_df)
            st.download_button("JPG", jpg, "lista.jpg", use_container_width=True)

    st.dataframe(lista_df, use_container_width=True, hide_index=True)
    st.metric("Custo estimado (R$)", custo_total)


def mostrar_lista_familia(lista_semanas):
    listas = []
    custo_total = 0

    for semana in lista_semanas:
        if not semana:
            continue
        lista_df, custo = calcular_lista_compras(semana)
        listas.append(lista_df)
        custo_total += custo

    if not listas:
        st.warning("Nenhuma lista disponivel.")
        return

    lista_total = pd.concat(listas)
    lista_total = lista_total.groupby(["Alimento", "Unidade"], as_index=False).agg(
        {"Quantidade": "sum", "Custo estimado (R$)": "sum"}
    )

    col_titulo, col_menu = st.columns([8, 1])
    with col_titulo:
        st.subheader("Lista de Compras - Familia")

    with col_menu:
        with st.popover("Exportar", use_container_width=True):
            csv = lista_total.to_csv(index=False).encode("utf-8")
            st.download_button("CSV", csv, "familia.csv", use_container_width=True)

            pdf = gerar_pdf_lista(lista_total, "Lista de Compras - Familia")
            st.download_button("PDF", pdf, "familia.pdf", use_container_width=True)

            jpg = gerar_jpg_lista(lista_total)
            st.download_button("JPG", jpg, "familia.jpg", use_container_width=True)

    st.dataframe(lista_total, use_container_width=True, hide_index=True)
    st.metric("Custo total familia (R$)", round(custo_total, 2))

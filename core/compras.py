"""
core/compras.py
-------------------------------------------------------
Responsável por calcular:

- Lista de compras consolidada
- Quantidades totais (kg ou unidades)
- Custo estimado total

Este módulo:
- NÃO acessa banco
- Recebe semana já gerada
- Trabalha apenas com os dicionários do cardápio

Estrutura esperada dos alimentos:
{
    "nome": str,
    "g": int,
    "preco": float   # preço por kg
}
-------------------------------------------------------
"""

import pandas as pd
from config import PRECO_OVO


def calcular_lista_compras(semana):
    """
    Recebe semana gerada pelo gerador.

    Retorna:
    - DataFrame da lista
    - custo_total (float)
    """

    totais = {}
    ovos_total = 0
    rap10_total = 0
    custo_total = 0

    # =====================================================
    # PERCORRER SEMANA
    # =====================================================

    for d in semana:

        for refeicao_nome in ["Almoço", "Jantar"]:

            ref = d[refeicao_nome]

            # ---------------- PROTEÍNA ----------------

            proteina = ref["proteina"]

            if isinstance(proteina, dict) and proteina.get("tipo") == "ovos":

                ovos_total += proteina["quantidade"]

            else:
                nome = proteina["nome"]
                gramas = proteina.get("g", 0)
                preco_kg = proteina.get("preco", 0)

                totais.setdefault(nome, {
                    "gramas": 0,
                    "preco_kg": preco_kg
                })

                totais[nome]["gramas"] += gramas

            # ---------------- CARBO ----------------

            carbo = ref["carbo"]

            nome = carbo["nome"]
            gramas = carbo.get("g", 0)
            preco_kg = carbo.get("preco", 0)

            totais.setdefault(nome, {
                "gramas": 0,
                "preco_kg": preco_kg
            })

            totais[nome]["gramas"] += gramas

            # ---------------- LEGUME ----------------

            if "legume" in ref:
                leg = ref["legume"]

                nome = leg["nome"]
                gramas = leg.get("g", 0)
                preco_kg = leg.get("preco", 0)

                totais.setdefault(nome, {
                    "gramas": 0,
                    "preco_kg": preco_kg
                })

                totais[nome]["gramas"] += gramas

        # ---------------- LANCHE ----------------

        if d["Lanche"].get("tipo") == "rap10":
            rap10_total += 1

    # =====================================================
    # MONTAR LISTA FINAL
    # =====================================================

    lista = []

    for nome, dados_item in totais.items():

        kg = dados_item["gramas"] / 1000
        custo = kg * dados_item["preco_kg"]

        custo_total += custo

        lista.append({
            "Alimento": nome,
            "Quantidade": round(kg, 2),
            "Unidade": "kg",
            "Custo estimado (R$)": round(custo, 2)
        })

    # =====================================================
    # OVOS
    # =====================================================

    if ovos_total:
        custo_ovos = ovos_total * PRECO_OVO
        custo_total += custo_ovos

        lista.append({
            "Alimento": "Ovos",
            "Quantidade": ovos_total,
            "Unidade": "un",
            "Custo estimado (R$)": round(custo_ovos, 2)
        })

    # =====================================================
    # RAP10 (preço fixo simples por unidade)
    # =====================================================

    if rap10_total:
        preco_un = 3.50  # ← pode futuramente virar config
        custo_rap = rap10_total * preco_un
        custo_total += custo_rap

        lista.append({
            "Alimento": "Rap10",
            "Quantidade": rap10_total,
            "Unidade": "un",
            "Custo estimado (R$)": round(custo_rap, 2)
        })

    return pd.DataFrame(lista), round(custo_total, 2)
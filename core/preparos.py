"""
core/preparos.py
-------------------------------------------------------
Responsável por formatar o nome final das refeições.
Compatível com nova modelagem.
-------------------------------------------------------
"""

import random
from config import PREPARO_FRANGO, PREPARO_CARBO


def _obter_gramas(item):
    """
    Compatível com:
    - g
    - gramas
    - ausência de peso
    """
    return item.get("g") or item.get("gramas") or 0


def aplicar_preparo(refeicao):

    proteina = refeicao["proteina"]
    carbo = refeicao["carbo"]

    # =====================================================
    # PROTEÍNA
    # =====================================================

    if isinstance(proteina, dict) and proteina.get("tipo") == "ovos":

        nome_proteina = f"Omelete ({proteina['quantidade']} ovos)"

    elif isinstance(proteina, dict) and "Frango" in proteina.get("nome", ""):

        preparo = random.choice(PREPARO_FRANGO)
        peso = _obter_gramas(proteina)

        nome_proteina = f"Frango {preparo} ({peso}g)" if peso else f"Frango {preparo}"

    elif isinstance(proteina, dict) and "Hamb" in proteina.get("nome", ""):

        peso = _obter_gramas(proteina)
        nome_proteina = f"Hambúrguer Grelhado ({peso}g)" if peso else "Hambúrguer Grelhado"

    else:
        nome_proteina = proteina.get("nome", "Proteína")

    # =====================================================
    # CARBO
    # =====================================================

    nome_carbo_base = carbo.get("nome", "")
    peso_carbo = _obter_gramas(carbo)

    if "Batata" in nome_carbo_base:

        preparo = random.choice(PREPARO_CARBO["Batata"])
        nome_carbo = (
            f"Batata {preparo} ({peso_carbo}g)"
            if peso_carbo else f"Batata {preparo}"
        )

    elif "Mandioca" in nome_carbo_base:

        preparo = random.choice(PREPARO_CARBO["Mandioca"])
        nome_carbo = (
            f"Mandioca {preparo} ({peso_carbo}g)"
            if peso_carbo else f"Mandioca {preparo}"
        )

    elif "Macarr" in nome_carbo_base:

        opcoes_macarrao = PREPARO_CARBO.get("Macarrão") or PREPARO_CARBO.get("Macarrao", ["Simples"])
        preparo = random.choice(opcoes_macarrao)
        nome_carbo = (
            f"Macarrão {preparo} ({peso_carbo}g)"
            if peso_carbo else f"Macarrão {preparo}"
        )

    else:
        nome_carbo = (
            f"{nome_carbo_base} ({peso_carbo}g)"
            if peso_carbo else nome_carbo_base
        )

    # =====================================================
    # SALVAR FORMATADOS
    # =====================================================

    refeicao["proteina_formatada"] = nome_proteina
    refeicao["carbo_formatado"] = nome_carbo

    return refeicao

"""
core/preparos.py
-------------------------------------------------------
Formata o nome final das refeicoes.
Usa preparos customizados por alimento quando existirem.
-------------------------------------------------------
"""

import random

from config import PREPARO_CARBO, PREPARO_FRANGO


def _obter_gramas(item):
    return item.get("g") or item.get("gramas") or 0


def _escolher_preparo(item, fallback):
    opcoes = item.get("preparos") or fallback
    return random.choice(opcoes)


def aplicar_preparo(refeicao):
    proteina = refeicao["proteina"]
    carbo = refeicao["carbo"]

    if isinstance(proteina, dict) and proteina.get("tipo") == "ovos":
        nome_proteina = f"Omelete ({proteina['quantidade']} ovos)"
    elif isinstance(proteina, dict) and "Frango" in proteina.get("nome", ""):
        preparo = _escolher_preparo(proteina, PREPARO_FRANGO)
        peso = _obter_gramas(proteina)
        nome_proteina = f"Frango {preparo} ({peso}g)" if peso else f"Frango {preparo}"
    elif isinstance(proteina, dict) and "Hamb" in proteina.get("nome", ""):
        preparo = _escolher_preparo(proteina, ["Grelhado"])
        peso = _obter_gramas(proteina)
        nome_proteina = f"Hamburguer {preparo} ({peso}g)" if peso else f"Hamburguer {preparo}"
    else:
        nome_proteina = proteina.get("nome", "Proteina")

    nome_carbo_base = carbo.get("nome", "")
    peso_carbo = _obter_gramas(carbo)

    if "Batata" in nome_carbo_base:
        preparo = _escolher_preparo(carbo, PREPARO_CARBO["Batata"])
        nome_carbo = f"Batata {preparo} ({peso_carbo}g)" if peso_carbo else f"Batata {preparo}"
    elif "Mandioca" in nome_carbo_base:
        preparo = _escolher_preparo(carbo, PREPARO_CARBO["Mandioca"])
        nome_carbo = f"Mandioca {preparo} ({peso_carbo}g)" if peso_carbo else f"Mandioca {preparo}"
    elif "Macarr" in nome_carbo_base:
        fallback = PREPARO_CARBO.get("Macarrao") or PREPARO_CARBO.get("Macarrão", ["Simples"])
        preparo = _escolher_preparo(carbo, fallback)
        nome_carbo = f"Macarrao {preparo} ({peso_carbo}g)" if peso_carbo else f"Macarrao {preparo}"
    else:
        nome_carbo = f"{nome_carbo_base} ({peso_carbo}g)" if peso_carbo else nome_carbo_base

    refeicao["proteina_formatada"] = nome_proteina
    refeicao["carbo_formatado"] = nome_carbo
    return refeicao

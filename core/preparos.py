"""
core/preparos.py
-------------------------------------------------------
Responsável por formatar o nome final das refeições,
incluindo tipo de preparo e exibição de peso.

Este módulo:
- NÃO acessa banco
- NÃO altera estrutura base da refeição
- Apenas adiciona campos formatados para exibição

Campos adicionados:
- proteina_formatada
- carbo_formatado
-------------------------------------------------------
"""

import random
from config import PREPARO_FRANGO, PREPARO_CARBO


def aplicar_preparo(refeicao):
    """
    Recebe dicionário:
    {
        "proteina": {...},
        "carbo": {...},
        "legume": {...} (opcional)
    }

    Retorna o mesmo dicionário com:
    - proteina_formatada
    - carbo_formatado
    """

    proteina = refeicao["proteina"]
    carbo = refeicao["carbo"]

    # =====================================================
    # PROTEÍNA
    # =====================================================

    if isinstance(proteina, dict) and proteina.get("tipo") == "ovos":

        nome_proteina = f"Omelete ({proteina['quantidade']} ovos)"

    elif isinstance(proteina, dict) and "Frango" in proteina.get("nome", ""):

        preparo = random.choice(PREPARO_FRANGO)
        peso = proteina.get("g", 0)

        nome_proteina = f"Frango {preparo} ({peso}g)"

    elif isinstance(proteina, dict) and "Hamb" in proteina.get("nome", ""):

        peso = proteina.get("g", 0)
        nome_proteina = f"Hambúrguer Grelhado ({peso}g)"

    else:
        nome_proteina = proteina.get("nome", "Proteína")

    # =====================================================
    # CARBO
    # =====================================================

    nome_carbo_base = carbo.get("nome", "")
    peso_carbo = carbo.get("g", 0)

    if "Batata" in nome_carbo_base:

        preparo = random.choice(PREPARO_CARBO["Batata"])
        nome_carbo = f"Batata {preparo} ({peso_carbo}g)"

    elif "Mandioca" in nome_carbo_base:

        preparo = random.choice(PREPARO_CARBO["Mandioca"])
        nome_carbo = f"Mandioca {preparo} ({peso_carbo}g)"

    elif "Macarr" in nome_carbo_base:

        preparo = random.choice(PREPARO_CARBO["Macarrao"])
        nome_carbo = f"Macarrão {preparo} ({peso_carbo}g)"

    else:
        nome_carbo = f"{nome_carbo_base} ({peso_carbo}g)"

    # =====================================================
    # SALVAR CAMPOS FORMATADOS
    # =====================================================

    refeicao["proteina_formatada"] = nome_proteina
    refeicao["carbo_formatado"] = nome_carbo

    return refeicao
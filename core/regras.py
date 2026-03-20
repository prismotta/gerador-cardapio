"""
core/regras.py
-------------------------------------------------------
Regras de combinacao entre proteina e carboidrato.
-------------------------------------------------------
"""


REGRAS_COMBINACAO = {
    "Ovos": {"Macarrao", "Mandioca"},
    "Hamburguer": {"Macarrao"},
}


def identificar_tipo_proteina(proteina):
    if not isinstance(proteina, dict):
        return None

    if proteina.get("tipo") == "ovos":
        return "Ovos"

    nome = proteina.get("nome", "")

    if "Hamb" in nome:
        return "Hamburguer"
    if "Frango" in nome:
        return "Frango"
    return nome


def identificar_tipo_carbo(nome_carbo):
    if "Macarr" in nome_carbo:
        return "Macarrao"
    if "Mandioca" in nome_carbo:
        return "Mandioca"
    if "Batata" in nome_carbo:
        return "Batata"
    return nome_carbo


def aplicar_regras_inteligentes(proteina, carbos):
    tipo_proteina = identificar_tipo_proteina(proteina)
    if not tipo_proteina:
        return carbos

    proibidos = REGRAS_COMBINACAO.get(tipo_proteina)
    if not proibidos:
        return carbos

    carbos_filtrados = [
        c for c in carbos
        if identificar_tipo_carbo(c) not in proibidos
    ]

    return carbos_filtrados if carbos_filtrados else carbos

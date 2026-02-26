"""
core/regras.py
-------------------------------------------------------
Módulo responsável pelas regras inteligentes de
combinação entre proteína e carboidrato.

Este módulo:
- NÃO acessa banco
- NÃO depende de chave por morador
- Trabalha apenas com nomes base

Exemplo de carbos recebidos:
["Batata", "Macarrao", "Mandioca"]
-------------------------------------------------------
"""

# =========================================================
# REGRAS DE COMBINAÇÃO
# =========================================================

REGRAS_COMBINACAO = {
    "Ovos": ["Macarrao", "Mandioca"],
    "Hambúrguer": ["Macarrao"],
}


# =========================================================
# IDENTIFICAR TIPO DA PROTEÍNA
# =========================================================

def identificar_tipo_proteina(proteina):
    """
    Determina o tipo base da proteína.
    """

    if not isinstance(proteina, dict):
        return None

    if proteina.get("tipo") == "ovos":
        return "Ovos"

    nome = proteina.get("nome", "")

    if "Hamb" in nome:
        return "Hambúrguer"

    if "Frango" in nome:
        return "Frango"

    return nome


# =========================================================
# FUNÇÃO PRINCIPAL
# =========================================================

def aplicar_regras_inteligentes(proteina, carbos):

    tipo_proteina = identificar_tipo_proteina(proteina)

    if not tipo_proteina:
        return carbos

    proibidos = REGRAS_COMBINACAO.get(tipo_proteina)

    # Se não houver regra
    if not proibidos:
        return carbos

    carbos_filtrados = [
        c for c in carbos
        if not any(p in c for p in proibidos)
    ]

    # Nunca retorna lista vazia
    return carbos_filtrados if carbos_filtrados else carbos
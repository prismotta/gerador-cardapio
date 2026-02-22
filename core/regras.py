"""
core/regras.py
-------------------------------------------------------
Módulo responsável pelas regras inteligentes de
combinação entre proteína e carboidrato.

Função:
- Impedir combinações indesejadas
- Centralizar lógica de restrições
- Permitir expansão futura (ex: regras por usuário)

Este módulo NÃO acessa banco.
Apenas aplica lógica sobre listas recebidas.
-------------------------------------------------------
"""

# =========================================================
# REGRAS DE COMBINAÇÃO
# =========================================================

"""
Estrutura:

{
    "Tipo_Proteina": ["Carbo_Proibido_1", "Carbo_Proibido_2"]
}

Importante:
Os valores devem corresponder ao padrão usado
nas chaves de carboidrato (ex: "Macarrao_M1").
"""

REGRAS_COMBINACAO = {
    "Ovos": ["Macarrao", "Mandioca"],
    "Hambúrguer": ["Macarrao"],
}


# =========================================================
# FUNÇÃO PRINCIPAL
# =========================================================

def aplicar_regras_inteligentes(proteina, carbos):
    """
    Aplica regras de restrição entre proteína e carboidratos.

    Parâmetros:
    - proteina: dict (ex: {"nome": "Frango", "g": 220})
    - carbos: lista de chaves de carboidrato

    Retorna:
    - Lista filtrada de carbos
    """

    # Segurança defensiva
    if not isinstance(proteina, dict):
        return carbos

    # =====================================================
    # IDENTIFICAR TIPO DE PROTEÍNA
    # =====================================================

    if proteina.get("tipo") == "ovos":
        tipo_proteina = "Ovos"
    else:
        nome = proteina.get("nome", "")

        if "Hamb" in nome:
            tipo_proteina = "Hambúrguer"
        elif "Frango" in nome:
            tipo_proteina = "Frango"
        else:
            tipo_proteina = nome

    # =====================================================
    # OBTER REGRAS
    # =====================================================

    proibidos = REGRAS_COMBINACAO.get(tipo_proteina)

    # Se não houver regra para essa proteína
    if not proibidos:
        return carbos

    # =====================================================
    # FILTRAR CARBOS
    # =====================================================

    carbos_filtrados = [
        c for c in carbos
        if not any(proibido in c for proibido in proibidos)
    ]

    # Fallback de segurança
    # Nunca deixamos lista vazia para evitar crash
    return carbos_filtrados if carbos_filtrados else carbos
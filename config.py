"""
config.py
-------------------------------------------------------
Arquivo central de configuracoes globais da aplicacao.

Este arquivo NAO deve conter dados dinamicos.
Alimentos sao controlados pelo banco de dados.
-------------------------------------------------------
"""

import os

# =========================================================
# BANCO DE DADOS
# =========================================================

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_PATH = "database/alimentos.db"

# =========================================================
# LIMITES DE CARBO
# =========================================================

LIMITES_CARBO = {
    "Macarrao": 4,
    "Mandioca": 4,
    "Batata": 6,
}

# =========================================================
# PREPAROS
# =========================================================

PREPARO_FRANGO = [
    "Grelhado na Frigideira",
    "Desfiado na Pressao",
    "Na Airfryer",
]

PREPARO_CARBO = {
    "Batata": [
        "Frita na Airfryer",
        "Assada na Airfryer",
        "Rustica na Airfryer",
    ],
    "Mandioca": [
        "Cozida",
    ],
    "Macarrao": [
        "Simples",
    ],
}

# =========================================================
# LEGUMES DISPONIVEIS
# =========================================================

LEGUMES = ["Pepino", "Tomate", "Cenoura"]

# =========================================================
# PRECOS FIXOS
# =========================================================

PRECO_OVO = 1.30

# =========================================================
# METAS DIARIAS
# =========================================================

META_PESO_DIARIO = {
    "Morador 1 (Massa)": 2000,
    "Morador 2 (Emagrecer)": 1400,
}

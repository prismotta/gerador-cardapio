"""
config.py
-------------------------------------------------------
Arquivo central de configurações globais da aplicação.

Este arquivo NÃO deve conter dados dinâmicos.
Alimentos são controlados pelo banco de dados.
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
    "Batata": 6
}

# =========================================================
# PREPAROS
# =========================================================

PREPARO_FRANGO = [
    "Grelhado na Frigideira",
    "Desfiado na Pressão",
    "Na Airfryer"
]

PREPARO_CARBO = {
    "Batata": [
        "Frita na Airfryer",
        "Assada na Airfryer",
        "Rústica na Airfryer"
    ],
    "Mandioca": [
        "Cozida",
        "Frita na Airfryer"
    ],
    "Macarrao": [
        "Simples"
    ]
}

# =========================================================
# LEGUMES DISPONÍVEIS
# =========================================================

LEGUMES = ["Pepino", "Tomate", "Cenoura"]

# =========================================================
# PREÇOS FIXOS
# =========================================================

PRECO_OVO = 1.30

# =========================================================
# METAS DIÁRIAS
# =========================================================

META_PESO_DIARIO = {
    "Morador 1 (Massa)": 2000,
    "Morador 2 (Emagrecer)": 1400
}
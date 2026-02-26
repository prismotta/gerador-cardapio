"""
database/db.py
-------------------------------------------------------
Camada de acesso a dados do sistema.

Nova modelagem normalizada:
- usuarios
- moradores
- alimentos
- porcoes

Sem duplicação de alimentos.
Compatível com SQLite e PostgreSQL.
-------------------------------------------------------
"""

import sqlite3
import hashlib
from urllib.parse import urlparse
from config import DATABASE_URL, DATABASE_PATH

try:
    import psycopg2
except ImportError:
    psycopg2 = None


# =========================================================
# CONEXÃO
# =========================================================

def get_connection():
    if DATABASE_URL:
        if not psycopg2:
            raise RuntimeError("psycopg2 não instalado.")

        result = urlparse(DATABASE_URL)

        return psycopg2.connect(
            dbname=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port,
        )

    return sqlite3.connect(DATABASE_PATH)


def is_postgres():
    return bool(DATABASE_URL)


def get_placeholder():
    return "%s" if is_postgres() else "?"


# =========================================================
# CRIAÇÃO DE TABELAS
# =========================================================

def criar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()

    id_type = (
        "SERIAL PRIMARY KEY"
        if is_postgres()
        else "INTEGER PRIMARY KEY AUTOINCREMENT"
    )

    # USUÁRIOS
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS usuarios (
            id {id_type},
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            tipo TEXT DEFAULT 'comum'
        )
    """)

    # MORADORES
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS moradores (
            id {id_type},
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            meta_calorica INTEGER NOT NULL,
            UNIQUE(usuario_id, nome)
        )
    """)

    # ALIMENTOS (SEM DUPLICAÇÃO)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS alimentos (
            id {id_type},
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            UNIQUE(usuario_id, nome)
        )
    """)

    # PORÇÕES (liga morador ao alimento)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS porcoes (
            id {id_type},
            morador_id INTEGER NOT NULL,
            alimento_id INTEGER NOT NULL,
            gramas INTEGER NOT NULL,
            UNIQUE(morador_id, alimento_id)
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# SEGURANÇA
# =========================================================

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


# =========================================================
# USUÁRIOS
# =========================================================

def criar_usuario(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()

    senha_hash = hash_senha(password)

    try:
        cursor.execute(
            f"""
            INSERT INTO usuarios (username, password)
            VALUES ({placeholder}, {placeholder})
            """,
            (username, senha_hash),
        )
        conn.commit()

        # Recupera ID do usuário criado
        cursor.execute(
            f"""
            SELECT id FROM usuarios
            WHERE username = {placeholder}
            """,
            (username,),
        )
        usuario_id = cursor.fetchone()[0]

        onboarding_inicial(usuario_id)

        return True

    except Exception:
        return False
    finally:
        conn.close()


def autenticar_usuario(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()

    senha_hash = hash_senha(password)

    cursor.execute(
        f"""
        SELECT id, username
        FROM usuarios
        WHERE username = {placeholder}
        AND password = {placeholder}
        """,
        (username, senha_hash),
    )

    usuario = cursor.fetchone()
    conn.close()
    return usuario


# =========================================================
# ONBOARDING
# =========================================================

def obter_alimentos_padrao():
    return {
        "Frango": 18.98,
        "Hambúrguer": 22,
        "Batata": 7,
        "Macarrão": 6.68,
        "Mandioca": 8,
        "Pepino": 6,
        "Tomate": 8,
        "Cenoura": 5,
    }


def obter_moradores_padrao():
    return {
        "Morador 1": 2000,
        "Morador 2": 1400,
    }


def onboarding_inicial(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()

    # Moradores
    for nome, meta in obter_moradores_padrao().items():
        if is_postgres():
            cursor.execute(
                f"""
                INSERT INTO moradores (usuario_id, nome, meta_calorica)
                VALUES ({placeholder}, {placeholder}, {placeholder})
                ON CONFLICT DO NOTHING
                """,
                (usuario_id, nome, meta),
            )
        else:
            cursor.execute(
                f"""
                INSERT OR IGNORE INTO moradores (usuario_id, nome, meta_calorica)
                VALUES ({placeholder}, {placeholder}, {placeholder})
                """,
                (usuario_id, nome, meta),
            )

    # Alimentos
    for nome, preco in obter_alimentos_padrao().items():
        if is_postgres():
            cursor.execute(
                f"""
                INSERT INTO alimentos (usuario_id, nome, preco)
                VALUES ({placeholder}, {placeholder}, {placeholder})
                ON CONFLICT DO NOTHING
                """,
                (usuario_id, nome, preco),
            )
        else:
            cursor.execute(
                f"""
                INSERT OR IGNORE INTO alimentos (usuario_id, nome, preco)
                VALUES ({placeholder}, {placeholder}, {placeholder})
                """,
                (usuario_id, nome, preco),
            )

    conn.commit()
    conn.close()
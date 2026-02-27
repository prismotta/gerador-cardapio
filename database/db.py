"""
database/db.py
-------------------------------------------------------
Camada de acesso a dados do sistema.
Compativel com SQLite e PostgreSQL.
-------------------------------------------------------
"""

import hashlib
import sqlite3
from urllib.parse import urlparse

from config import DATABASE_PATH, DATABASE_URL

try:
    import psycopg2
except ImportError:
    psycopg2 = None


def get_connection():
    if DATABASE_URL:
        if not psycopg2:
            raise RuntimeError("psycopg2 nao instalado.")

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


def criar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()

    id_type = "SERIAL PRIMARY KEY" if is_postgres() else "INTEGER PRIMARY KEY AUTOINCREMENT"

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS usuarios (
            id {id_type},
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            tipo TEXT DEFAULT 'comum'
        )
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS moradores (
            id {id_type},
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            meta_calorica INTEGER NOT NULL,
            UNIQUE(usuario_id, nome)
        )
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS alimentos (
            id {id_type},
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            UNIQUE(usuario_id, nome)
        )
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS porcoes (
            id {id_type},
            morador_id INTEGER NOT NULL,
            alimento_id INTEGER NOT NULL,
            gramas INTEGER NOT NULL,
            UNIQUE(morador_id, alimento_id)
        )
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS preparos_alimento (
            id {id_type},
            alimento_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            UNIQUE(alimento_id, nome)
        )
        """
    )

    # Regra global: mandioca deve ter apenas preparo "Cozida".
    cursor.execute(
        f"""
        DELETE FROM preparos_alimento
        WHERE nome = {placeholder}
          AND alimento_id IN (
              SELECT id
              FROM alimentos
              WHERE nome = {placeholder}
          )
        """,
        ("Frita na Airfryer", "Mandioca"),
    )
    cursor.execute(
        f"""
        DELETE FROM preparos_alimento
        WHERE nome IN ({placeholder}, {placeholder})
          AND alimento_id IN (
              SELECT id
              FROM alimentos
              WHERE nome = {placeholder}
          )
        """,
        ("Frita na Airfrier", "Frita na Ayrfrier", "Mandioca"),
    )

    conn.commit()
    conn.close()


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


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
    return {"Morador 1": 2000, "Morador 2": 1400}


def obter_preparos_padrao():
    return {
        "Frango": ["Grelhado na Frigideira", "Desfiado na Pressao", "Na Airfryer"],
        "Hambúrguer": ["Grelhado"],
        "Batata": ["Frita na Airfryer", "Assada na Airfryer", "Rustica na Airfryer"],
        "Macarrão": ["Simples"],
        "Mandioca": ["Cozida"],
        "Pepino": ["Cru em rodelas"],
        "Tomate": ["Cru em rodelas"],
        "Cenoura": ["Crua ralada"],
    }


def onboarding_inicial(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()

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

    cursor.execute(
        f"""
        SELECT id, nome
        FROM alimentos
        WHERE usuario_id = {placeholder}
        """,
        (usuario_id,),
    )
    alimentos_usuario = cursor.fetchall()
    alimento_por_nome = {nome: alimento_id for alimento_id, nome in alimentos_usuario}

    for nome_alimento, preparos in obter_preparos_padrao().items():
        alimento_id = alimento_por_nome.get(nome_alimento)
        if not alimento_id:
            continue
        for preparo in preparos:
            if is_postgres():
                cursor.execute(
                    f"""
                    INSERT INTO preparos_alimento (alimento_id, nome)
                    VALUES ({placeholder}, {placeholder})
                    ON CONFLICT DO NOTHING
                    """,
                    (alimento_id, preparo),
                )
            else:
                cursor.execute(
                    f"""
                    INSERT OR IGNORE INTO preparos_alimento (alimento_id, nome)
                    VALUES ({placeholder}, {placeholder})
                    """,
                    (alimento_id, preparo),
                )

    conn.commit()
    conn.close()

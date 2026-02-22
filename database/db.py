"""
database/db.py
-------------------------------------------------------
Camada de acesso a dados do sistema.

Responsável por:
- Conexão com SQLite (local) ou PostgreSQL (produção)
- Criação de tabelas
- Autenticação de usuários
- CRUD de alimentos
- Auto onboarding (inserção padrão inicial)

Compatível com:
- Ambiente local (SQLite)
- Render + Neon (PostgreSQL)

Arquitetura:
App → db.py → Banco
-------------------------------------------------------
"""

import sqlite3
import psycopg2
import hashlib
from urllib.parse import urlparse
from config import DATABASE_URL, DATABASE_PATH


# =========================================================
# CONEXÃO
# =========================================================

def get_connection():
    """
    Retorna conexão ativa com o banco.

    - Se DATABASE_URL existir → conecta em PostgreSQL
    - Caso contrário → usa SQLite local
    """
    if DATABASE_URL:
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
    """Verifica se o ambiente atual é PostgreSQL."""
    return bool(DATABASE_URL)


def get_placeholder():
    """
    Retorna o placeholder correto para queries parametrizadas.

    PostgreSQL usa: %s  
    SQLite usa: ?
    """
    return "%s" if is_postgres() else "?"


# =========================================================
# CRIAÇÃO DE TABELAS
# =========================================================

def criar_tabelas():
    """
    Cria as tabelas principais do sistema caso não existam.
    Executado ao iniciar o app.
    """
    conn = get_connection()
    cursor = conn.cursor()

    id_type = "SERIAL PRIMARY KEY" if is_postgres() else "INTEGER PRIMARY KEY AUTOINCREMENT"

    # Tabela de usuários
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS usuarios (
            id {id_type},
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            tipo TEXT DEFAULT 'comum'
        )
    """)

    # Tabela de alimentos
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS alimentos (
            id {id_type},
            usuario_id INTEGER NOT NULL,
            chave TEXT NOT NULL,
            nome TEXT NOT NULL,
            gramas INTEGER NOT NULL,
            preco REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# SEGURANÇA
# =========================================================

def hash_senha(senha):
    """
    Gera hash SHA-256 da senha.
    Nunca armazenamos senha em texto puro.
    """
    return hashlib.sha256(senha.encode()).hexdigest()


# =========================================================
# USUÁRIOS
# =========================================================

def criar_usuario(username, password):
    """
    Cria novo usuário.

    Retorna:
    - True se sucesso
    - False se usuário já existir
    """
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
        return True
    except Exception:
        return False
    finally:
        conn.close()


def autenticar_usuario(username, password):
    """
    Autentica usuário.
    Retorna (id, username) ou None.
    """
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
# ALIMENTOS - CRUD
# =========================================================

def inserir_alimento(usuario_id, chave, nome, gramas, preco):
    """Insere novo alimento."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()

    cursor.execute(
        f"""
        INSERT INTO alimentos (usuario_id, chave, nome, gramas, preco)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """,
        (usuario_id, chave, nome, gramas, preco),
    )

    conn.commit()
    conn.close()


def listar_alimentos_usuario(usuario_id):
    """Retorna lista de alimentos do usuário."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()

    cursor.execute(
        f"""
        SELECT chave, nome, gramas, preco
        FROM alimentos
        WHERE usuario_id = {placeholder}
        """,
        (usuario_id,),
    )

    dados = cursor.fetchall()
    conn.close()
    return dados


def carregar_alimentos_dict(usuario_id):
    """
    Retorna alimentos no formato dicionário:
    {
        "Frango_M1": {"nome": "...", "g": ..., "preco": ...}
    }
    """
    alimentos = listar_alimentos_usuario(usuario_id)
    resultado = {}

    for chave, nome, gramas, preco in alimentos:
        resultado[chave] = {
            "nome": nome,
            "g": gramas,
            "preco": preco
        }

    return resultado


def atualizar_alimento(usuario_id, chave, nome, gramas, preco):
    """Atualiza alimento existente."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()

    cursor.execute(
        f"""
        UPDATE alimentos
        SET nome = {placeholder},
            gramas = {placeholder},
            preco = {placeholder}
        WHERE usuario_id = {placeholder}
        AND chave = {placeholder}
        """,
        (nome, gramas, preco, usuario_id, chave),
    )

    conn.commit()
    conn.close()


def deletar_alimento(usuario_id, chave):
    """Remove alimento."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()

    cursor.execute(
        f"""
        DELETE FROM alimentos
        WHERE usuario_id = {placeholder}
        AND chave = {placeholder}
        """,
        (usuario_id, chave),
    )

    conn.commit()
    conn.close()


def obter_alimento_por_chave(usuario_id, chave):
    """Retorna um alimento específico."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()

    cursor.execute(
        f"""
        SELECT chave, nome, gramas, preco
        FROM alimentos
        WHERE usuario_id = {placeholder}
        AND chave = {placeholder}
        """,
        (usuario_id, chave),
    )

    dado = cursor.fetchone()
    conn.close()

    return dado


# =========================================================
# AUTO ONBOARDING
# =========================================================

def inserir_alimentos_padrao(usuario_id):
    """
    Insere alimentos padrão para novo usuário.
    Executado apenas na primeira entrada.
    """
    alimentos_padrao = {
        "Frango_M1": ("Frango", 220, 18.98),
        "Frango_M2": ("Frango", 150, 18.98),
        "Hamburguer_M1": ("Hambúrguer", 300, 22),
        "Hamburguer_M2": ("Hambúrguer", 150, 22),
        "Batata_M1": ("Batata", 300, 7),
        "Batata_M2": ("Batata", 180, 7),
        "Macarrao_M1": ("Macarrão", 130, 6.68),
        "Macarrao_M2": ("Macarrão", 80, 6.68),
        "Mandioca_M1": ("Mandioca", 300, 8),
        "Mandioca_M2": ("Mandioca", 200, 8),
    }

    for chave, (nome, g, preco) in alimentos_padrao.items():
        inserir_alimento(usuario_id, chave, nome, g, preco)


def garantir_alimentos_iniciais(usuario_id):
    """
    Garante que o usuário tenha alimentos cadastrados.
    Se não tiver, insere os padrões automaticamente.
    """
    alimentos = listar_alimentos_usuario(usuario_id)

    if not alimentos:
        inserir_alimentos_padrao(usuario_id)
"""
database/sessao.py
-------------------------------------------------------
Gerenciamento de sessão persistente do usuário.

Responsável por:
- Salvar dados de sessão em arquivo JSON
- Carregar dados de sessão anteriores
- Limpar sessão ao fazer logout

Segurança:
- Armazena apenas username (sem senha)
- Usa hashing para validação
-------------------------------------------------------
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Tuple

# Caminho do arquivo de sessão persistente
SESSAO_PATH = Path(__file__).parent.parent / ".sessao.json"


def _hash_username(username: str) -> str:
    """Gera hash do username para validação."""
    return hashlib.sha256(username.encode()).hexdigest()[:16]


def salvar_sessao(usuario_id: int, username: str) -> None:
    """
    Salva dados da sessão atual em arquivo.
    
    Args:
        usuario_id: ID do usuário
        username: Nome de usuário
    """
    dados = {
        "usuario_id": usuario_id,
        "username": username,
        "hash": _hash_username(username)
    }
    
    try:
        with open(SESSAO_PATH, "w") as f:
            json.dump(dados, f)
    except Exception as e:
        print(f"Erro ao salvar sessão: {e}")


def carregar_sessao() -> Optional[Tuple[int, str]]:
    """
    Carrega dados da sessão anterior.
    
    Returns:
        Tupla (usuario_id, username) se sessão válida, senão None
    """
    if not SESSAO_PATH.exists():
        return None
    
    try:
        with open(SESSAO_PATH, "r") as f:
            dados = json.load(f)
        
        usuario_id = dados.get("usuario_id")
        username = dados.get("username")
        hash_salvo = dados.get("hash")
        
        # Validar integridade
        if hash_salvo != _hash_username(username):
            limpar_sessao()
            return None
        
        return (usuario_id, username)
    
    except Exception as e:
        print(f"Erro ao carregar sessão: {e}")
        return None


def limpar_sessao() -> None:
    """Remove arquivo de sessão persistente."""
    try:
        if SESSAO_PATH.exists():
            SESSAO_PATH.unlink()
    except Exception as e:
        print(f"Erro ao limpar sessão: {e}")

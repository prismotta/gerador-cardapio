"""
core/gerador.py
-------------------------------------------------------
Responsável por toda lógica de geração do cardápio semanal.
-------------------------------------------------------
"""

import random
from typing import Dict, List, Tuple, Set
from config import LIMITES_CARBO, LEGUMES
from core.regras import aplicar_regras_inteligentes
from core.preparos import aplicar_preparo


# =========================================================
# AUXILIAR
# =========================================================

def extrair_id_refeicao(ref: Dict) -> Tuple[str, str]:
    """Extrai identificador único da refeição.
    
    Args:
        ref: Dicionário de refeição com proteína e carbo
        
    Returns:
        Tupla (proteina_nome, carbo_nome) para comparação
    """
    proteina = ref.get("proteina", {})
    carbo = ref.get("carbo", {})
    
    proteina_nome = proteina.get("nome", "Ovos") if isinstance(proteina, dict) else "Ovos"
    carbo_nome = carbo.get("nome", "") if isinstance(carbo, dict) else ""
    
    return (proteina_nome, carbo_nome)


def gerar_recheios_rap10() -> str:
    """Gera string de recheios para RAP10.
    
    Returns:
        String com recheios aleatórios (1-2 itens)
    """
    recheios = random.sample(
        ["Frango Desfiado", "Presunto", "Queijo"],
        k=random.choice([1, 2])
    )
    return "Rap10 + " + " + ".join(recheios)


# =========================================================
# PROTEÍNA
# =========================================================

def gerar_proteina(morador_atual: str, config_local: Dict, alimentos: Dict) -> Dict:
    """Seleciona proteína para refeição.
    
    Args:
        morador_atual: Identificador do morador
        config_local: Configurações locais do morador
        alimentos: Dicionário de alimentos disponíveis
        
    Returns:
        Dicionário com proteína selecionada
    """

    if morador_atual == "Morador 1 (Massa)":
        frango = "Frango_M1"
        hamburguer = "Hamburguer_M1"
    else:
        frango = "Frango_M2"
        hamburguer = "Hamburguer_M2"

    opcoes = ["OVOS", frango, hamburguer]

    if config_local["modo_economico"]:
        escolha = random.choices(opcoes, weights=[0.4, 0.3, 0.3], k=1)[0]
    else:
        escolha = random.choice(opcoes)

    if escolha == "OVOS":
        return {
            "tipo": "ovos",
            "quantidade": config_local["ovos_refeicao"]
        }

    if escolha not in alimentos:
        raise KeyError(f"Alimento '{escolha}' não encontrado no banco.")

    return alimentos[escolha]


# =========================================================
# REFEIÇÃO FIXA
# =========================================================

def gerar_refeicao_fixa(
    tipo_proteina: str,
    morador_atual: str,
    config_local: Dict,
    incluir_legume: bool,
    contador_carbo: Dict,
    alimentos: Dict
) -> Dict:
    """Gera refeição principal (almoço/jantar).
    
    Args:
        tipo_proteina: Tipo de proteína (Ovos, Frango, Hambúrguer)
        morador_atual: Identificador do morador
        config_local: Configurações locais
        incluir_legume: Se deve incluir legume
        contador_carbo: Contador de carboidratos usados
        alimentos: Dicionário de alimentos
        
    Returns:
        Dicionário com refeição completa formatada
    """

    # ---------------- PROTEÍNA ----------------

    if tipo_proteina == "Ovos":
        proteina = {
            "tipo": "ovos",
            "quantidade": config_local["ovos_refeicao"]
        }

    elif tipo_proteina == "Frango":
        chave = "Frango_M1" if morador_atual == "Morador 1 (Massa)" else "Frango_M2"
        proteina = alimentos.get(chave)

    else:
        chave = "Hamburguer_M1" if morador_atual == "Morador 1 (Massa)" else "Hamburguer_M2"
        proteina = alimentos.get(chave)

    if not proteina:
        raise KeyError(f"Proteína '{tipo_proteina}' não encontrada.")

    # ---------------- CARBO ----------------

    if morador_atual == "Morador 1 (Massa)":
        carbos = ["Batata_M1", "Macarrao_M1", "Mandioca_M1"]
    else:
        carbos = ["Batata_M2", "Macarrao_M2", "Mandioca_M2"]

    carbos = aplicar_regras_inteligentes(proteina, carbos)

    carbos_filtrados = [
        c for c in carbos
        if (
            ("Macarrao" in c and contador_carbo["Macarrao"] < LIMITES_CARBO["Macarrao"]) or
            ("Mandioca" in c and contador_carbo["Mandioca"] < LIMITES_CARBO["Mandioca"]) or
            ("Batata" in c and contador_carbo["Batata"] < LIMITES_CARBO["Batata"])
        )
    ]

    if not carbos_filtrados:
        carbos_filtrados = carbos

    carbo_key = random.choice(carbos_filtrados)

    if carbo_key not in alimentos:
        raise KeyError(f"Carbo '{carbo_key}' não encontrado.")

    carbo = alimentos[carbo_key]

    if "Macarrao" in carbo_key:
        contador_carbo["Macarrao"] += 1
    elif "Mandioca" in carbo_key:
        contador_carbo["Mandioca"] += 1
    elif "Batata" in carbo_key:
        contador_carbo["Batata"] += 1

    refeicao = {
        "proteina": proteina,
        "carbo": carbo
    }

    # ---------------- LEGUME (CORRIGIDO) ----------------

    if incluir_legume:
        legumes_disponiveis = [l for l in LEGUMES if l in alimentos]

        if legumes_disponiveis:
            legume_key = random.choice(legumes_disponiveis)
            refeicao["legume"] = alimentos[legume_key]

    # 🔥 ESSENCIAL
    return aplicar_preparo(refeicao)


# =========================================================
# LANCHE
# =========================================================

def gerar_lanche(morador_atual: str, forcar_rap10: bool = False) -> Dict:
    """Gera opção de lanche.
    
    Args:
        morador_atual: Identificador do morador
        forcar_rap10: Se True, força RAP10 como lanche
        
    Returns:
        Dicionário com tipo e nome do lanche
    """
    # Se forçar RAP10, gerar e retornar
    if forcar_rap10:
        lanche_rap10 = gerar_recheios_rap10()
        return {
            "tipo": "rap10",
            "nome": lanche_rap10
        }

    opcoes = []
    pesos = []

    if morador_atual == "Morador 1 (Massa)":
        opcoes += [
            "Banana + Aveia",
            "Sanduíche Presunto + Mussarela",
            "Pão + Banana + Pasta de Amendoim"
        ]
        pesos += [2, 2, 2]

        variacao = random.choice(["Leite", "Pasta de Amendoim"])

        if variacao == "Leite":
            opcoes.append("Vitamina de Banana + Aveia + Leite")
        else:
            opcoes.append("Vitamina de Banana + Aveia + Pasta de Amendoim")

        pesos.append(2)

    else:
        opcoes += [
            "Banana + Aveia",
            "Vitamina de Banana + Aveia"
        ]
        pesos += [3, 3]
        opcoes.append("Sanduíche Presunto + Mussarela")
        pesos.append(1)

    lanche_escolhido = random.choices(opcoes, weights=pesos, k=1)[0]

    return {
        "tipo": "rap10" if lanche_escolhido.startswith("Rap10") else "simples",
        "nome": lanche_escolhido
    }


# =========================================================
# CARDÁPIO SEMANAL
# =========================================================

def gerar_cardapio(morador_atual: str, config_local: Dict, alimentos: Dict) -> List[Dict]:
    """Gera cardápio completo para uma semana.
    
    Args:
        morador_atual: Identificador do morador
        config_local: Configurações locais do morador  
        alimentos: Dicionário de alimentos disponíveis
        
    Returns:
        Lista com 7 dias de cardápio (almoço, lanche, jantar)
    """
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    semana = []
    
    # Selecionar 2 dias aleatórios da semana para RAP10
    dias_com_rap10: Set[int] = set(random.sample(range(7), k=2))

    proteinas_semana = (
        ["Frango"] * 6 +
        ["Hambúrguer"] * 4 +
        ["Ovos"] * 4
    )

    random.shuffle(proteinas_semana)

    contador_carbo = {
        "Macarrao": 0,
        "Mandioca": 0,
        "Batata": 0
    }

    incluir_legume = morador_atual == "Morador 2 (Emagrecer)"
    ultima_refeicao_id = None

    for idx, dia in enumerate(dias):

        # ================= ALMOÇO =================
        while True:

            if not proteinas_semana:
                raise ValueError("Proteínas insuficientes.")

            tipo_proteina = random.choice(proteinas_semana)

            almoco = gerar_refeicao_fixa(
                tipo_proteina,
                morador_atual,
                config_local,
                incluir_legume,
                contador_carbo,
                alimentos
            )

            id_atual = extrair_id_refeicao(almoco)

            if id_atual != ultima_refeicao_id:
                proteinas_semana.remove(tipo_proteina)
                break

        ultima_refeicao_id = id_atual

        # ================= LANCHE =================
        forcar_rap10 = idx in dias_com_rap10
        lanche = gerar_lanche(morador_atual, forcar_rap10)

        ultima_refeicao_id = ("lanche", lanche["nome"])

        # ================= JANTAR =================
        while True:

            if not proteinas_semana:
                raise ValueError("Proteínas insuficientes.")

            tipo_proteina = random.choice(proteinas_semana)

            jantar = gerar_refeicao_fixa(
                tipo_proteina,
                morador_atual,
                config_local,
                incluir_legume,
                contador_carbo,
                alimentos
            )

            id_atual = extrair_id_refeicao(jantar)

            if id_atual != ultima_refeicao_id:
                proteinas_semana.remove(tipo_proteina)
                break

        ultima_refeicao_id = id_atual

        semana.append({
            "Dia": dia,
            "Almoço": almoco,
            "Lanche": lanche,
            "Jantar": jantar
        })

    return semana
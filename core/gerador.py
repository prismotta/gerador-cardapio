"""
core/gerador.py
-------------------------------------------------------
Responsável por toda lógica de geração do cardápio semanal.
-------------------------------------------------------
"""

import random
from config import LIMITES_CARBO, LEGUMES
from core.regras import aplicar_regras_inteligentes
from core.preparos import aplicar_preparo


# =========================================================
# AUXILIAR
# =========================================================

def extrair_id_refeicao(ref):
    proteina_nome = ref["proteina"].get("nome", "Ovos")
    carbo_nome = ref["carbo"].get("nome", "")
    return (proteina_nome, carbo_nome)


# =========================================================
# PROTEÍNA
# =========================================================

def gerar_proteina(morador_atual, config_local, alimentos):

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
    tipo_proteina,
    morador_atual,
    config_local,
    incluir_legume,
    contador_carbo,
    alimentos
):

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

def gerar_lanche(morador_atual, rap10_count, limite_rap10, forcar_rap10=False):

    # Se forçar RAP10, gerar e retornar
    if forcar_rap10:
        recheios = random.sample(
            ["Frango Desfiado", "Presunto", "Queijo"],
            k=random.choice([1, 2])
        )
        lanche_rap10 = "Rap10 + " + " + ".join(recheios)
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

    if rap10_count < limite_rap10:
        recheios = random.sample(
            ["Frango Desfiado", "Presunto", "Queijo"],
            k=random.choice([1, 2])
        )
        opcoes.append("Rap10 + " + " + ".join(recheios))
        pesos.append(1)

    lanche_escolhido = random.choices(opcoes, weights=pesos, k=1)[0]

    return {
        "tipo": "rap10" if lanche_escolhido.startswith("Rap10") else "simples",
        "nome": lanche_escolhido
    }


# =========================================================
# CARDÁPIO SEMANAL
# =========================================================

def gerar_cardapio(morador_atual, config_local, limite_rap10, alimentos):

    dias = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]
    semana = []
    rap10_count = 0

    # Selecionar 2 dias aleatórios da semana para RAP10
    dias_com_rap10 = set(random.sample(range(7), k=2))

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
        lanche = gerar_lanche(morador_atual, rap10_count, limite_rap10, forcar_rap10)

        if lanche["tipo"] == "rap10":
            rap10_count += 1

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
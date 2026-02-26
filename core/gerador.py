"""
core/gerador.py
-------------------------------------------------------
Gerador de cardápio compatível com nova modelagem:

- alimentos (únicos)
- moradores
- porcoes

Sem duplicação.
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


def organizar_alimentos_por_nome(alimentos):
    """
    Converte lista [(id, nome, preco)]
    em dict { nome: {id, nome, preco} }
    """
    resultado = {}
    for alimento_id, nome, preco in alimentos:
        resultado[nome] = {
            "id": alimento_id,
            "nome": nome,
            "preco": preco
        }
    return resultado


# =========================================================
# REFEIÇÃO FIXA
# =========================================================

def gerar_refeicao_fixa(
    tipo_proteina,
    incluir_legume,
    contador_carbo,
    alimentos_dict
):

    # ---------------- PROTEÍNA ----------------

    if tipo_proteina == "Ovos":
        proteina = {
            "tipo": "ovos",
            "quantidade": 3
        }

    else:
        if tipo_proteina not in alimentos_dict:
            raise KeyError(f"Proteína '{tipo_proteina}' não encontrada.")

        proteina = alimentos_dict[tipo_proteina]

    # ---------------- CARBO ----------------

    carbos_base = ["Batata", "Macarrão", "Mandioca"]

    carbos = aplicar_regras_inteligentes(proteina, carbos_base)

    carbos_filtrados = [
        c for c in carbos
        if (
            ("Macarrão" in c and contador_carbo["Macarrão"] < LIMITES_CARBO["Macarrão"]) or
            ("Mandioca" in c and contador_carbo["Mandioca"] < LIMITES_CARBO["Mandioca"]) or
            ("Batata" in c and contador_carbo["Batata"] < LIMITES_CARBO["Batata"])
        )
    ]

    if not carbos_filtrados:
        carbos_filtrados = carbos

    carbo_nome = random.choice(carbos_filtrados)

    if carbo_nome not in alimentos_dict:
        raise KeyError(f"Carbo '{carbo_nome}' não encontrado.")

    carbo = alimentos_dict[carbo_nome]

    contador_carbo[carbo_nome] += 1

    refeicao = {
        "proteina": proteina,
        "carbo": carbo
    }

    # ---------------- LEGUME ----------------

    if incluir_legume:
        legumes_disponiveis = [
            l for l in LEGUMES
            if l in alimentos_dict
        ]

        if legumes_disponiveis:
            legume_nome = random.choice(legumes_disponiveis)
            refeicao["legume"] = alimentos_dict[legume_nome]

    return aplicar_preparo(refeicao)


# =========================================================
# LANCHE
# =========================================================

def gerar_lanche(rap10_count, limite_rap10):

    opcoes = [
        "Banana + Aveia",
        "Sanduíche Presunto + Mussarela",
        "Pão + Banana + Pasta de Amendoim",
        "Vitamina de Banana + Aveia"
    ]

    pesos = [3, 2, 2, 2]

    if rap10_count < limite_rap10:
        recheios = random.sample(
            ["Frango Desfiado", "Presunto", "Queijo"],
            k=random.choice([1, 2])
        )
        opcoes.append("Rap10 + " + " + ".join(recheios))
        pesos.append(1)

    escolhido = random.choices(opcoes, weights=pesos, k=1)[0]

    return {
        "tipo": "rap10" if escolhido.startswith("Rap10") else "simples",
        "nome": escolhido
    }


# =========================================================
# CARDÁPIO SEMANAL
# =========================================================

def gerar_cardapio(morador_id, alimentos):

    dias = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]
    semana = []
    rap10_count = 0

    alimentos_dict = organizar_alimentos_por_nome(alimentos)

    proteinas_semana = (
        ["Frango"] * 6 +
        ["Hambúrguer"] * 4 +
        ["Ovos"] * 4
    )

    random.shuffle(proteinas_semana)

    contador_carbo = {
        "Macarrão": 0,
        "Mandioca": 0,
        "Batata": 0
    }

    incluir_legume = True
    ultima_refeicao_id = None

    for dia in dias:

        # ================= ALMOÇO =================
        while True:

            if not proteinas_semana:
                raise ValueError("Proteínas insuficientes.")

            tipo_proteina = random.choice(proteinas_semana)

            almoco = gerar_refeicao_fixa(
                tipo_proteina,
                incluir_legume,
                contador_carbo,
                alimentos_dict
            )

            id_atual = extrair_id_refeicao(almoco)

            if id_atual != ultima_refeicao_id:
                proteinas_semana.remove(tipo_proteina)
                break

        ultima_refeicao_id = id_atual

        # ================= LANCHE =================
        lanche = gerar_lanche(rap10_count, limite_rap10=3)

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
                incluir_legume,
                contador_carbo,
                alimentos_dict
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

# =========================================================
# REGENERAÇÃO PARCIAL
# =========================================================

def regenerar_almoco(semana, dia_index, alimentos):

    alimentos_dict = organizar_alimentos_por_nome(alimentos)

    contador_carbo = {
        "Macarrão": 0,
        "Mandioca": 0,
        "Batata": 0
    }

    incluir_legume = True

    tipo_proteina = random.choice(["Frango", "Hambúrguer", "Ovos"])

    novo_almoco = gerar_refeicao_fixa(
        tipo_proteina,
        incluir_legume,
        contador_carbo,
        alimentos_dict
    )

    semana[dia_index]["Almoço"] = novo_almoco
    return semana


def regenerar_lanche(semana, dia_index):

    rap10_count = sum(
        1 for d in semana
        if d["Lanche"].get("tipo") == "rap10"
    )

    novo_lanche = gerar_lanche(rap10_count, limite_rap10=3)

    semana[dia_index]["Lanche"] = novo_lanche
    return semana


def regenerar_jantar(semana, dia_index, alimentos):

    alimentos_dict = organizar_alimentos_por_nome(alimentos)

    contador_carbo = {
        "Macarrão": 0,
        "Mandioca": 0,
        "Batata": 0
    }

    incluir_legume = True

    tipo_proteina = random.choice(["Frango", "Hambúrguer", "Ovos"])

    novo_jantar = gerar_refeicao_fixa(
        tipo_proteina,
        incluir_legume,
        contador_carbo,
        alimentos_dict
    )

    semana[dia_index]["Jantar"] = novo_jantar
    return semana
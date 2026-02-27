"""
core/gerador.py
-------------------------------------------------------
Gerador de cardapio compativel com modelagem:
- alimentos
- moradores
- porcoes
-------------------------------------------------------
"""

import random
from config import LIMITES_CARBO, LEGUMES
from core.regras import aplicar_regras_inteligentes
from core.preparos import aplicar_preparo


def extrair_id_refeicao(ref):
    proteina_nome = ref["proteina"].get("nome", "Ovos")
    carbo_nome = ref["carbo"].get("nome", "")
    return (proteina_nome, carbo_nome)


def organizar_alimentos_por_nome(alimentos):
    resultado = {}
    for alimento_id, nome, preco in alimentos:
        resultado[nome] = {"id": alimento_id, "nome": nome, "preco": preco}
    return resultado


def identificar_tipo_carbo(nome_carbo):
    if "Macarr" in nome_carbo:
        return "Macarrao"
    if "Mandioca" in nome_carbo:
        return "Mandioca"
    if "Batata" in nome_carbo:
        return "Batata"
    return nome_carbo


def obter_limite_carbo(tipo_carbo):
    if tipo_carbo == "Macarrao":
        return LIMITES_CARBO.get("Macarrao", LIMITES_CARBO.get("Macarrão", 999))
    return LIMITES_CARBO.get(tipo_carbo, 999)


def encontrar_alimento_por_nome(alimentos_dict, nome_base):
    if nome_base in alimentos_dict:
        return alimentos_dict[nome_base]

    if nome_base == "Hamburguer":
        for candidato in ("Hambúrguer", "Hamburguer"):
            if candidato in alimentos_dict:
                return alimentos_dict[candidato]

    if nome_base == "Macarrao":
        for candidato in ("Macarrão", "Macarrao"):
            if candidato in alimentos_dict:
                return alimentos_dict[candidato]

    return None


def gerar_refeicao_fixa(tipo_proteina, incluir_legume, contador_carbo, alimentos_dict):
    if tipo_proteina == "Ovos":
        proteina = {"tipo": "ovos", "quantidade": 3}
    else:
        proteina = encontrar_alimento_por_nome(alimentos_dict, tipo_proteina)
        if not proteina:
            raise KeyError(f"Proteina '{tipo_proteina}' nao encontrada.")

    carbos_base = ["Batata", "Macarrão", "Mandioca"]
    carbos = aplicar_regras_inteligentes(proteina, carbos_base)

    carbos_filtrados = []
    for carbo_nome in carbos:
        tipo_carbo = identificar_tipo_carbo(carbo_nome)
        if contador_carbo[tipo_carbo] < obter_limite_carbo(tipo_carbo):
            carbos_filtrados.append(carbo_nome)

    if not carbos_filtrados:
        carbos_filtrados = carbos

    carbo_nome = random.choice(carbos_filtrados)
    carbo = encontrar_alimento_por_nome(alimentos_dict, carbo_nome)
    if not carbo:
        raise KeyError(f"Carbo '{carbo_nome}' nao encontrado.")

    contador_carbo[identificar_tipo_carbo(carbo_nome)] += 1

    refeicao = {"proteina": proteina, "carbo": carbo}

    if incluir_legume:
        legumes_disponiveis = [l for l in LEGUMES if l in alimentos_dict]
        if legumes_disponiveis:
            legume_nome = random.choice(legumes_disponiveis)
            refeicao["legume"] = alimentos_dict[legume_nome]

    return aplicar_preparo(refeicao)


def gerar_lanche(rap10_count, limite_rap10):
    opcoes = [
        "Banana + Aveia",
        "Sanduíche Presunto + Mussarela",
        "Pão + Banana + Pasta de Amendoim",
        "Vitamina de Banana + Aveia",
    ]
    pesos = [3, 2, 2, 2]

    if rap10_count < limite_rap10:
        recheios = random.sample(["Frango Desfiado", "Presunto", "Queijo"], k=random.choice([1, 2]))
        opcoes.append("Rap10 + " + " + ".join(recheios))
        pesos.append(1)

    escolhido = random.choices(opcoes, weights=pesos, k=1)[0]
    return {"tipo": "rap10" if escolhido.startswith("Rap10") else "simples", "nome": escolhido}


def _contador_inicial_carbo():
    return {"Macarrao": 0, "Mandioca": 0, "Batata": 0}


def gerar_cardapio(morador_id, alimentos):
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    semana = []
    rap10_count = 0

    alimentos_dict = organizar_alimentos_por_nome(alimentos)

    proteinas_semana = (["Frango"] * 6 + ["Hamburguer"] * 4 + ["Ovos"] * 4)
    random.shuffle(proteinas_semana)

    contador_carbo = _contador_inicial_carbo()
    incluir_legume = True
    ultima_refeicao_id = None

    for dia in dias:
        while True:
            if not proteinas_semana:
                raise ValueError("Proteinas insuficientes.")

            tipo_proteina = random.choice(proteinas_semana)
            almoco = gerar_refeicao_fixa(tipo_proteina, incluir_legume, contador_carbo, alimentos_dict)
            id_atual = extrair_id_refeicao(almoco)

            if id_atual != ultima_refeicao_id:
                proteinas_semana.remove(tipo_proteina)
                break

        ultima_refeicao_id = id_atual
        lanche = gerar_lanche(rap10_count, limite_rap10=3)
        if lanche["tipo"] == "rap10":
            rap10_count += 1

        ultima_refeicao_id = ("lanche", lanche["nome"])

        while True:
            if not proteinas_semana:
                raise ValueError("Proteinas insuficientes.")

            tipo_proteina = random.choice(proteinas_semana)
            jantar = gerar_refeicao_fixa(tipo_proteina, incluir_legume, contador_carbo, alimentos_dict)
            id_atual = extrair_id_refeicao(jantar)

            if id_atual != ultima_refeicao_id:
                proteinas_semana.remove(tipo_proteina)
                break

        ultima_refeicao_id = id_atual
        semana.append({"Dia": dia, "Almoço": almoco, "Lanche": lanche, "Jantar": jantar})

    return semana


def regenerar_almoco(semana, dia_index, alimentos):
    alimentos_dict = organizar_alimentos_por_nome(alimentos)
    tipo_proteina = random.choice(["Frango", "Hamburguer", "Ovos"])
    novo_almoco = gerar_refeicao_fixa(tipo_proteina, True, _contador_inicial_carbo(), alimentos_dict)
    semana[dia_index]["Almoço"] = novo_almoco
    return semana


def regenerar_lanche(semana, dia_index):
    rap10_count = sum(1 for d in semana if d["Lanche"].get("tipo") == "rap10")
    semana[dia_index]["Lanche"] = gerar_lanche(rap10_count, limite_rap10=3)
    return semana


def regenerar_jantar(semana, dia_index, alimentos):
    alimentos_dict = organizar_alimentos_por_nome(alimentos)
    tipo_proteina = random.choice(["Frango", "Hamburguer", "Ovos"])
    novo_jantar = gerar_refeicao_fixa(tipo_proteina, True, _contador_inicial_carbo(), alimentos_dict)
    semana[dia_index]["Jantar"] = novo_jantar
    return semana

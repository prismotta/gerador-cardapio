"""
core/gerador.py
-------------------------------------------------------
Gerador de cardapio compativel com:
- alimentos
- moradores
- porcoes por morador
-------------------------------------------------------
"""

import random

from config import LEGUMES, LIMITES_CARBO
from core.preparos import aplicar_preparo
from core.regras import aplicar_regras_inteligentes

KEY_ALMOCO = "Almo\u00e7o"

GRAMAS_PADRAO = {
    "Frango": 150,
    "Hamburguer": 120,
    "Macarrao": 140,
    "Mandioca": 180,
    "Batata": 180,
    "Pepino": 80,
    "Tomate": 80,
    "Cenoura": 80,
}


def extrair_id_refeicao(ref):
    proteina_nome = ref["proteina"].get("nome", "Ovos")
    carbo_nome = ref["carbo"].get("nome", "")
    return (proteina_nome, carbo_nome)


def inferir_gramas_padrao(nome):
    if "Frango" in nome:
        return GRAMAS_PADRAO["Frango"]
    if "Hamb" in nome:
        return GRAMAS_PADRAO["Hamburguer"]
    if "Macarr" in nome:
        return GRAMAS_PADRAO["Macarrao"]
    if "Mandioca" in nome:
        return GRAMAS_PADRAO["Mandioca"]
    if "Batata" in nome:
        return GRAMAS_PADRAO["Batata"]
    if "Pepino" in nome:
        return GRAMAS_PADRAO["Pepino"]
    if "Tomate" in nome:
        return GRAMAS_PADRAO["Tomate"]
    if "Cenoura" in nome:
        return GRAMAS_PADRAO["Cenoura"]
    return 100


def organizar_alimentos_por_nome(alimentos):
    resultado = {}
    for item in alimentos:
        if isinstance(item, dict):
            alimento_id = item["id"]
            nome = item["nome"]
            preco = item["preco"]
            preparos = item.get("preparos", [])
            # None = sem configuracao por morador, usa padrao.
            # 0 = restricao (nao consumir).
            gramas_custom = item.get("gramas")
            gramas = inferir_gramas_padrao(nome) if gramas_custom is None else int(gramas_custom)
        else:
            alimento_id, nome, preco = item
            preparos = []
            gramas = inferir_gramas_padrao(nome)

        resultado[nome] = {
            "id": alimento_id,
            "nome": nome,
            "preco": preco,
            "gramas": gramas,
            "preparos": preparos,
        }
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
        return LIMITES_CARBO.get("Macarrao", LIMITES_CARBO.get("Macarr\u00e3o", 999))
    return LIMITES_CARBO.get(tipo_carbo, 999)


def alimento_habilitado(item):
    return int(item.get("gramas", 0)) > 0


def encontrar_alimento_por_nome(alimentos_dict, nome_base):
    if nome_base in alimentos_dict:
        return alimentos_dict[nome_base]

    if nome_base == "Hamburguer":
        for candidato in ("Hamb\u00farguer", "Hamburguer"):
            if candidato in alimentos_dict:
                return alimentos_dict[candidato]

    if nome_base == "Macarrao":
        for candidato in ("Macarr\u00e3o", "Macarrao"):
            if candidato in alimentos_dict:
                return alimentos_dict[candidato]

    return None


def _carbos_disponiveis(alimentos_dict):
    candidatos = ["Batata", "Macarr\u00e3o", "Mandioca"]
    validos = []
    for nome in candidatos:
        item = encontrar_alimento_por_nome(alimentos_dict, nome)
        if item and alimento_habilitado(item):
            validos.append(nome)
    return validos


def gerar_refeicao_fixa(tipo_proteina, incluir_legume, contador_carbo, alimentos_dict):
    if tipo_proteina == "Ovos":
        proteina = {"tipo": "ovos", "quantidade": 3, "gramas": 150}
    else:
        proteina = encontrar_alimento_por_nome(alimentos_dict, tipo_proteina)
        if not proteina or not alimento_habilitado(proteina):
            raise KeyError(f"Proteina '{tipo_proteina}' nao disponivel para este morador.")

    carbos_base = _carbos_disponiveis(alimentos_dict)
    if not carbos_base:
        raise ValueError("Nenhum carbo disponivel para este morador.")

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
    if not carbo or not alimento_habilitado(carbo):
        raise KeyError(f"Carbo '{carbo_nome}' nao disponivel para este morador.")

    contador_carbo[identificar_tipo_carbo(carbo_nome)] += 1
    refeicao = {"proteina": proteina, "carbo": carbo}

    if incluir_legume:
        legumes_disponiveis = [
            nome for nome in LEGUMES
            if (nome in alimentos_dict and alimento_habilitado(alimentos_dict[nome]))
        ]
        if legumes_disponiveis:
            legume_nome = random.choice(legumes_disponiveis)
            refeicao["legume"] = alimentos_dict[legume_nome]

    return aplicar_preparo(refeicao)


def gerar_lanche(rap10_count, limite_rap10):
    opcoes = [
        "Banana + Aveia",
        "Sanduiche Presunto + Mussarela",
        "Pao + Banana + Pasta de Amendoim",
        "Vitamina de Banana + Aveia",
    ]
    pesos = [3, 2, 2, 2]

    if rap10_count < limite_rap10:
        recheios = random.sample(["Frango Desfiado", "Presunto", "Queijo"], k=random.choice([1, 2]))
        opcoes.append("Rap10 + " + " + ".join(recheios))
        pesos.append(1)

    escolhido = random.choices(opcoes, weights=pesos, k=1)[0]

    if escolhido.startswith("Rap10"):
        gramas = 140 if escolhido.count("+") >= 2 else 100
    elif "Vitamina" in escolhido:
        gramas = 300
    elif "Presunto" in escolhido and "Mussarela" in escolhido:
        gramas = 180
    elif "Pasta de Amendoim" in escolhido:
        gramas = 230
    else:
        gramas = 220

    return {
        "tipo": "rap10" if escolhido.startswith("Rap10") else "simples",
        "nome": escolhido,
        "gramas": gramas,
    }


def _contador_inicial_carbo():
    return {"Macarrao": 0, "Mandioca": 0, "Batata": 0}


def _opcoes_proteina(alimentos_dict):
    opcoes = []
    frango = encontrar_alimento_por_nome(alimentos_dict, "Frango")
    if frango and alimento_habilitado(frango):
        opcoes.extend(["Frango"] * 3)

    hamburguer = encontrar_alimento_por_nome(alimentos_dict, "Hamburguer")
    if hamburguer and alimento_habilitado(hamburguer):
        opcoes.extend(["Hamburguer"] * 2)

    # Ovos sempre disponiveis
    opcoes.extend(["Ovos"] * 2)
    return opcoes


def _montar_pool_semanal(alimentos_dict, total_refeicoes=14):
    opcoes = _opcoes_proteina(alimentos_dict)
    if not opcoes:
        return []
    return [random.choice(opcoes) for _ in range(total_refeicoes)]


def _escolher_proteina_almoco(proteinas_semana):
    if "Ovos" in proteinas_semana:
        return random.choice(proteinas_semana + ["Ovos", "Ovos"])
    return random.choice(proteinas_semana)


def gerar_cardapio(morador_id, alimentos):
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
    semana = []
    rap10_count = 0

    alimentos_dict = organizar_alimentos_por_nome(alimentos)
    proteinas_semana = _montar_pool_semanal(alimentos_dict, total_refeicoes=14)
    if len(proteinas_semana) < 14:
        raise ValueError("Proteinas insuficientes para gerar a semana desse morador.")

    random.shuffle(proteinas_semana)
    contador_carbo = _contador_inicial_carbo()
    incluir_legume = True
    ultima_refeicao_id = None

    for dia in dias:
        while True:
            if not proteinas_semana:
                raise ValueError("Proteinas insuficientes.")

            tipo_proteina = _escolher_proteina_almoco(proteinas_semana)
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
        semana.append({"Dia": dia, KEY_ALMOCO: almoco, "Lanche": lanche, "Jantar": jantar})

    return semana


def regenerar_almoco(semana, dia_index, alimentos):
    alimentos_dict = organizar_alimentos_por_nome(alimentos)
    opcoes = _opcoes_proteina(alimentos_dict)
    if not opcoes:
        raise ValueError("Sem proteinas disponiveis.")
    tipo_proteina = _escolher_proteina_almoco(opcoes)
    novo_almoco = gerar_refeicao_fixa(tipo_proteina, True, _contador_inicial_carbo(), alimentos_dict)
    semana[dia_index][KEY_ALMOCO] = novo_almoco
    return semana


def regenerar_lanche(semana, dia_index):
    rap10_count = sum(1 for d in semana if d["Lanche"].get("tipo") == "rap10")
    semana[dia_index]["Lanche"] = gerar_lanche(rap10_count, limite_rap10=3)
    return semana


def regenerar_jantar(semana, dia_index, alimentos):
    alimentos_dict = organizar_alimentos_por_nome(alimentos)
    opcoes = _opcoes_proteina(alimentos_dict)
    if not opcoes:
        raise ValueError("Sem proteinas disponiveis.")
    tipo_proteina = random.choice(opcoes)
    novo_jantar = gerar_refeicao_fixa(tipo_proteina, True, _contador_inicial_carbo(), alimentos_dict)
    semana[dia_index]["Jantar"] = novo_jantar
    return semana

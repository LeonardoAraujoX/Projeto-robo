"""Projeto do Robô — Entrega 1 (Grupo 06).

O robô sai do canto superior esquerdo da grade e precisa chegar ao canto
inferior direito andando só para a DIREITA ou para BAIXO, uma casa por vez.
O custo de uma rota é a soma de todas as casas visitadas (partida e chegada
incluídas). Casas com None (null no JSON) são obstáculos.

Funções principais (exigidas pelo enunciado):
    resolver(entrada)  -> lê o texto JSON, valida e devolve o resultado
    recursivo(mapa)    -> menor custo usando recursão pura (ou None se não há rota)
    guloso(mapa)       -> custo da regra gulosa (ou None se ela não chega)

Função auxiliar para a tarefa 5 (medição):
    contar_chamadas(mapa) -> (menor custo, número de chamadas recursivas)

Importante: NÃO há memoização. Nenhum resultado de chamada anterior é
guardado; cada casa é recalculada toda vez que uma rota passa por ela.
"""

import json

# Na grade, um obstáculo é representado por None (null no JSON).
OBSTACULO = None


# ---------------------------------------------------------------------------
# Validação da entrada
# ---------------------------------------------------------------------------
def validar_custos(custos):
    """Confere se `custos` é uma grade válida.

    Devolve None quando está tudo certo, ou um texto explicando o erro.
    Regras: lista não vazia de linhas; cada linha é uma lista não vazia;
    todas as linhas têm o mesmo tamanho; cada valor é inteiro positivo ou None.
    """
    if not isinstance(custos, list) or len(custos) == 0:
        return "'custos' deve ser uma lista não vazia de linhas"

    largura = len(custos[0]) if isinstance(custos[0], list) else None

    for i, linha in enumerate(custos):
        if not isinstance(linha, list) or len(linha) == 0:
            return f"a linha {i} deve ser uma lista não vazia"
        if len(linha) != largura:
            return (f"todas as linhas devem ter o mesmo tamanho "
                    f"(linha 0 tem {largura}, linha {i} tem {len(linha)})")
        for j, valor in enumerate(linha):
            if valor is OBSTACULO:
                continue
            # Em Python, True/False também são int; por isso excluímos bool.
            if isinstance(valor, bool) or not isinstance(valor, int):
                return (f"valor inválido na linha {i}, coluna {j}: "
                        f"{valor!r} (use inteiro positivo ou null)")
            if valor <= 0:
                return (f"valor inválido na linha {i}, coluna {j}: "
                        f"{valor} (o custo deve ser maior que zero)")
    return None


# ---------------------------------------------------------------------------
# Solução recursiva (tarefa 2)
# ---------------------------------------------------------------------------
class Contador:
    """Guarda apenas QUANTAS chamadas foram feitas (não guarda resultados)."""

    def __init__(self):
        self.chamadas = 0


def _menor_custo(mapa, linha, coluna, contador):
    """Menor custo para ir da casa (linha, coluna) até a chegada.

    Devolve None quando é impossível chegar a partir desta casa.
    """
    contador.chamadas += 1

    custo_casa = mapa[linha][coluna]

    # Caso base 1: obstáculo -> impossível.
    if custo_casa is OBSTACULO:
        return None

    ultima_linha = len(mapa) - 1
    ultima_coluna = len(mapa[0]) - 1

    # Caso base 2: chegada -> a resposta é o custo da própria casa.
    if linha == ultima_linha and coluna == ultima_coluna:
        return custo_casa

    # Caso recursivo: toda rota daqui começa indo para a direita OU para baixo.
    # Posições fora da grade contam como impossíveis, por isso só chamamos o
    # vizinho quando ele existe dentro da grade.
    melhor_resto = None

    if coluna < ultima_coluna:                       # existe casa à direita
        pela_direita = _menor_custo(mapa, linha, coluna + 1, contador)
        if pela_direita is not None:
            melhor_resto = pela_direita

    if linha < ultima_linha:                         # existe casa abaixo
        por_baixo = _menor_custo(mapa, linha + 1, coluna, contador)
        if por_baixo is not None and (melhor_resto is None or por_baixo < melhor_resto):
            melhor_resto = por_baixo

    # Nenhum dos dois caminhos chega: daqui também é impossível.
    if melhor_resto is None:
        return None

    return custo_casa + melhor_resto


def recursivo(mapa):
    """Menor custo da partida (0, 0) até a chegada, ou None se não há rota."""
    return _menor_custo(mapa, 0, 0, Contador())


def contar_chamadas(mapa):
    """Executa a mesma recursão e devolve (menor custo, número de chamadas)."""
    contador = Contador()
    custo = _menor_custo(mapa, 0, 0, contador)
    return custo, contador.chamadas


# ---------------------------------------------------------------------------
# Regra gulosa (tarefa 6)
# ---------------------------------------------------------------------------
def guloso(mapa):
    """Anda sempre para o vizinho livre mais barato (direita no empate).

    Devolve o custo total da rota escolhida, ou None se a partida for
    obstáculo ou se o robô ficar preso (sem vizinho livre) antes da chegada.
    """
    ultima_linha = len(mapa) - 1
    ultima_coluna = len(mapa[0]) - 1

    linha, coluna = 0, 0
    if mapa[0][0] is OBSTACULO:
        return None
    total = mapa[0][0]

    while not (linha == ultima_linha and coluna == ultima_coluna):
        direita = None
        baixo = None
        if coluna < ultima_coluna and mapa[linha][coluna + 1] is not OBSTACULO:
            direita = mapa[linha][coluna + 1]
        if linha < ultima_linha and mapa[linha + 1][coluna] is not OBSTACULO:
            baixo = mapa[linha + 1][coluna]

        if direita is None and baixo is None:
            return None                      # ficou preso: a regra não chega

        # "<=" faz a direita ganhar no empate.
        if direita is not None and (baixo is None or direita <= baixo):
            coluna += 1
            total += direita
        else:
            linha += 1
            total += baixo

    return total


# ---------------------------------------------------------------------------
# Função de contrato (tarefa 3)
# ---------------------------------------------------------------------------
def resolver(entrada):
    """Recebe o TEXTO JSON da entrada e devolve um dicionário de resultado.

    {"status": "ok", "custo": <inteiro>}
    {"status": "sem_caminho", "custo": None}
    {"status": "entrada_invalida", "erro": "<mensagem>"}
    """
    if not isinstance(entrada, str):
        return {"status": "entrada_invalida", "erro": "a entrada deve ser um texto JSON"}

    try:
        dados = json.loads(entrada)
    except (ValueError, RecursionError) as erro:
        return {"status": "entrada_invalida", "erro": f"JSON mal formado: {erro}"}

    if not isinstance(dados, dict):
        return {"status": "entrada_invalida",
                "erro": "a entrada deve ser um objeto JSON com a chave 'custos'"}
    if "custos" not in dados:
        return {"status": "entrada_invalida", "erro": "falta a chave 'custos'"}

    mensagem = validar_custos(dados["custos"])
    if mensagem is not None:
        return {"status": "entrada_invalida", "erro": mensagem}

    custo = recursivo(dados["custos"])
    if custo is None:
        return {"status": "sem_caminho", "custo": None}
    return {"status": "ok", "custo": custo}

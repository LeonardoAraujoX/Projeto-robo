"""Linha de comando do Projeto do Robô — Entrega 1 (Grupo 06).

Uso:
    python main.py                                -> demonstração completa
    python main.py '{"custos": [[1,2],[3,4]]}'    -> resolve o texto JSON informado
    python main.py --arquivo grade.json           -> resolve o JSON salvo em um arquivo
"""

import json
import sys

from projeto_robo import contar_chamadas, guloso, recursivo, resolver

N = None
GRADE_EXEMPLO = [
    [2, 1, 9, 9, 9],
    [3, N, 1, 1, 9],
    [1, 1, 1, N, 2],
    [9, 9, 1, 1, 1],
]
GRADE_GULOSA_ERRA = [[1, 1, 1], [2, 9, 9], [1, 1, 1]]
GRADE_GULOSA_ERRA_4X4 = [[1, 1, 1, 1], [2, 9, 9, 9], [1, 9, 9, 9], [1, 1, 1, 1]]
GRADE_GULOSA_PRESA = [[1, 1, 1], [5, 1, N], [5, 5, 1]]


def mostrar(custo):
    return "sem caminho" if custo is None else str(custo)


def demonstracao():
    print("=== Resultado de resolver() na grade do exemplo ===")
    print(json.dumps(resolver(json.dumps({"custos": GRADE_EXEMPLO}))))

    print("\n=== Exemplos próprios do grupo (tarefa 1) ===")
    sem_rota = '{"custos": [[3, 2, null], [4, null, 5], [null, 6, 1]]}'
    invalida = '{"custos": "1 2 3"}'
    print(sem_rota, "->", json.dumps(resolver(sem_rota), ensure_ascii=False))
    print(invalida, "->", json.dumps(resolver(invalida), ensure_ascii=False))

    print("\n=== Medição do trabalho (tarefa 5): chamadas recursivas ===")
    print(f"{'Grade':<10}{'Custo':>8}{'Chamadas':>12}")
    for linhas, colunas in [(2, 3), (3, 3), (6, 6), (10, 10), (1, 10)]:
        grade = [[1] * colunas for _ in range(linhas)]
        custo, chamadas = contar_chamadas(grade)
        print(f"{f'{linhas}x{colunas}':<10}{custo:>8}{chamadas:>12}")
    custo, chamadas = contar_chamadas(GRADE_EXEMPLO)
    print(f"{'Exemplo':<10}{custo:>8}{chamadas:>12}")

    print("\n=== Regra gulosa (tarefa 6) ===")
    for nome, grade in [("Grade do exemplo", GRADE_EXEMPLO),
                        ("Grade própria 4x4 (erra)", GRADE_GULOSA_ERRA_4X4),
                        ("Grade própria 3x3 (erra)", GRADE_GULOSA_ERRA),
                        ("Grade própria (fica presa)", GRADE_GULOSA_PRESA)]:
        print(f"{nome:<28} guloso = {mostrar(guloso(grade)):<12} "
              f"recursivo = {mostrar(recursivo(grade))}")


def main(argumentos):
    if not argumentos:
        demonstracao()
        return
    if argumentos[0] == "--arquivo" and len(argumentos) == 2:
        with open(argumentos[1], encoding="utf-8") as arquivo:
            entrada = arquivo.read()
    else:
        entrada = " ".join(argumentos)
    print(json.dumps(resolver(entrada), ensure_ascii=False))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # acentos no terminal do Windows
    main(sys.argv[1:])

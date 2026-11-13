"""Testes automáticos do Projeto do Robô — Entrega 1 (Grupo 06).

Rodar a partir da pasta do projeto:
    python -m unittest discover -s tests -v

As listas CASOS_PROFESSOR e CASOS_GRUPO também são usadas pelo gerador do
relatório, para que a tabela do PDF mostre exatamente o que foi testado.
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from projeto_robo import contar_chamadas, guloso, recursivo, resolver  # noqa: E402

N = None  # atalho para obstáculo

GRADE_EXEMPLO = [
    [2, 1, 9, 9, 9],
    [3, N, 1, 1, 9],
    [1, 1, 1, N, 2],
    [9, 9, 1, 1, 1],
]

# Grade própria em que a regra gulosa erra (tarefa 6).
GRADE_GULOSA_ERRA = [
    [1, 1, 1],
    [2, 9, 9],
    [1, 1, 1],
]

# Grade própria 4x4 em que a regra gulosa erra (tarefa 6, "grade de até 4x4").
GRADE_GULOSA_ERRA_4X4 = [
    [1, 1, 1, 1],
    [2, 9, 9, 9],
    [1, 9, 9, 9],
    [1, 1, 1, 1],
]

# Grade própria em que a regra gulosa fica presa, embora exista rota.
GRADE_GULOSA_PRESA = [
    [1, 1, 1],
    [5, 1, N],
    [5, 5, 1],
]


def texto(custos):
    """Monta o texto JSON de entrada a partir de uma grade Python."""
    return json.dumps({"custos": custos})


# (descrição, texto de entrada, status esperado, custo esperado)
# custo esperado = None quando o status não é "ok".
CASOS_PROFESSOR = [
    ("[[7]]", texto([[7]]), "ok", 7),
    ("[[1, 2, 3]]", texto([[1, 2, 3]]), "ok", 6),
    ("[[1], [2], [3]]", texto([[1], [2], [3]]), "ok", 6),
    ("[[1, 1, 1], [1, 1, 1]]", texto([[1, 1, 1], [1, 1, 1]]), "ok", 4),
    ("Grade do exemplo", texto(GRADE_EXEMPLO), "ok", 11),
    ("[[1, 1, null], [2, null, 1], [1, 1, 1]]", texto([[1, 1, N], [2, N, 1], [1, 1, 1]]), "ok", 6),
    ("[[null]]", texto([[N]]), "sem_caminho", None),
    ("[[null, 1], [1, 1]]", texto([[N, 1], [1, 1]]), "sem_caminho", None),
    ("[[1, 1], [1, null]]", texto([[1, 1], [1, N]]), "sem_caminho", None),
    ("[[1, null], [null, 1]]", texto([[1, N], [N, 1]]), "sem_caminho", None),
    ("custos = []", '{"custos": []}', "entrada_invalida", None),
    ("custos = [[]]", '{"custos": [[]]}', "entrada_invalida", None),
    ("custos = [[1, 2], [3]]", '{"custos": [[1, 2], [3]]}', "entrada_invalida", None),
    ("custos = [[true, 1]]", '{"custos": [[true, 1]]}', "entrada_invalida", None),
    ('custos = [["1", 1]]', '{"custos": [["1", 1]]}', "entrada_invalida", None),
    ("custos = [[1.5, 1]]", '{"custos": [[1.5, 1]]}', "entrada_invalida", None),
    ("custos = [[0, 1]]", '{"custos": [[0, 1]]}', "entrada_invalida", None),
    ("custos = [[-1, 1]]", '{"custos": [[-1, 1]]}', "entrada_invalida", None),
    ('Texto {"matriz": [[1]]}', '{"matriz": [[1]]}', "entrada_invalida", None),
    ("Texto [[1, 2]]", "[[1, 2]]", "entrada_invalida", None),
    ('Texto {"custos": [[1, 2]', '{"custos": [[1, 2]', "entrada_invalida", None),
]

CASOS_GRUPO = [
    # Exemplo próprio de entrada válida SEM rota (tarefa 1).
    ("Próprio: [[3, 2, null], [4, null, 5], [null, 6, 1]]",
     texto([[3, 2, N], [4, N, 5], [N, 6, 1]]), "sem_caminho", None),
    # Exemplo próprio de entrada INVÁLIDA (tarefa 1): custos não é lista.
    ('Próprio: {"custos": "1 2 3"}', '{"custos": "1 2 3"}', "entrada_invalida", None),
    # Grade 3x3 com rota única de menor custo 7 (1+3+1+1+1).
    ("Próprio: [[1, 3, 1], [1, 5, 1], [4, 2, 1]]",
     texto([[1, 3, 1], [1, 5, 1], [4, 2, 1]]), "ok", 7),
    # Uma linha inteira de obstáculos separa partida e chegada.
    ("Próprio: [[1, 1, 1], [null, null, null], [1, 1, 1]]",
     texto([[1, 1, 1], [N, N, N], [1, 1, 1]]), "sem_caminho", None),
    # Grade da regra gulosa: o melhor caminho desce primeiro e custa 6.
    ("Próprio: [[1, 1, 1], [2, 9, 9], [1, 1, 1]]", texto(GRADE_GULOSA_ERRA), "ok", 6),
    # Obstáculo na partida, mesmo com o resto livre.
    ("Próprio: [[null, 1, 1], [1, 1, 1]]", texto([[N, 1, 1], [1, 1, 1]]), "sem_caminho", None),
    # Chave 'custos' com valor null.
    ('Próprio: {"custos": null}', '{"custos": null}', "entrada_invalida", None),
    # Texto vazio.
    ("Próprio: texto vazio", "", "entrada_invalida", None),
]

# (linhas, colunas, chamadas esperadas) — tabela da tarefa 5.
MEDICOES_PROFESSOR = [
    (2, 3, 9),
    (3, 3, 19),
    (6, 6, 923),
    (10, 10, 184755),
    (1, 10, 10),
]

# Número de chamadas medido pelo grupo na grade do exemplo (com obstáculos).
CHAMADAS_GRADE_EXEMPLO = 43


def grade_de_uns(linhas, colunas):
    return [[1] * colunas for _ in range(linhas)]


class TestResolver(unittest.TestCase):
    def _conferir(self, casos):
        for descricao, entrada, status, custo in casos:
            with self.subTest(caso=descricao):
                resultado = resolver(entrada)
                self.assertEqual(resultado["status"], status)
                if status == "entrada_invalida":
                    self.assertIn("erro", resultado)
                    self.assertIsInstance(resultado["erro"], str)
                    self.assertTrue(resultado["erro"])
                    self.assertNotIn("custo", resultado)
                else:
                    self.assertEqual(resultado, {"status": status, "custo": custo})

    def test_casos_do_professor(self):
        self._conferir(CASOS_PROFESSOR)

    def test_casos_do_grupo(self):
        self._conferir(CASOS_GRUPO)

    def test_saida_sem_campo_caminho(self):
        # O campo 'caminho' fica para a Entrega 2.
        self.assertNotIn("caminho", resolver(texto(GRADE_EXEMPLO)))

    def test_entrada_que_nao_e_texto(self):
        self.assertEqual(resolver({"custos": [[1]]})["status"], "entrada_invalida")


class TestRecursivo(unittest.TestCase):
    def test_grade_do_exemplo(self):
        self.assertEqual(recursivo(GRADE_EXEMPLO), 11)

    def test_sem_rota_devolve_none(self):
        self.assertIsNone(recursivo([[1, N], [N, 1]]))

    def test_nao_altera_a_grade(self):
        copia = [linha[:] for linha in GRADE_EXEMPLO]
        recursivo(GRADE_EXEMPLO)
        self.assertEqual(GRADE_EXEMPLO, copia)


class TestMedicao(unittest.TestCase):
    def test_chamadas_nas_grades_de_uns(self):
        for linhas, colunas, esperado in MEDICOES_PROFESSOR:
            with self.subTest(grade=f"{linhas}x{colunas}"):
                _, chamadas = contar_chamadas(grade_de_uns(linhas, colunas))
                self.assertEqual(chamadas, esperado)

    def test_chamadas_na_grade_do_exemplo(self):
        custo, chamadas = contar_chamadas(GRADE_EXEMPLO)
        self.assertEqual(custo, 11)
        self.assertEqual(chamadas, CHAMADAS_GRADE_EXEMPLO)


class TestGuloso(unittest.TestCase):
    def test_grade_do_exemplo_da_26_contra_11(self):
        self.assertEqual(guloso(GRADE_EXEMPLO), 26)
        self.assertEqual(recursivo(GRADE_EXEMPLO), 11)

    def test_grade_propria_em_que_o_guloso_erra(self):
        self.assertEqual(guloso(GRADE_GULOSA_ERRA), 13)
        self.assertEqual(recursivo(GRADE_GULOSA_ERRA), 6)

    def test_grade_propria_4x4_em_que_o_guloso_erra(self):
        # Guloso: 1+1+1+1+9+9+1 = 23. Ótimo: 1+2+1+1+1+1+1 = 8.
        self.assertEqual(guloso(GRADE_GULOSA_ERRA_4X4), 23)
        self.assertEqual(recursivo(GRADE_GULOSA_ERRA_4X4), 8)

    def test_grade_propria_em_que_o_guloso_fica_preso(self):
        self.assertIsNone(guloso(GRADE_GULOSA_PRESA))
        self.assertEqual(recursivo(GRADE_GULOSA_PRESA), 9)

    def test_empate_prefere_a_direita(self):
        # Na partida, direita (2) e baixo (2) empatam. Indo para a direita o
        # total é 1+2+1+1 = 5; se fosse para baixo seria 1+2+9+1 = 13.
        self.assertEqual(guloso([[1, 2, 1], [2, 9, 1]]), 5)

    def test_partida_bloqueada(self):
        self.assertIsNone(guloso([[N, 1], [1, 1]]))

    def test_grade_de_uma_casa(self):
        self.assertEqual(guloso([[7]]), 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)

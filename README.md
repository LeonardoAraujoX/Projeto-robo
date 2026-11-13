# Projeto do Robô — Entrega 1 (Grupo 06)

Programa em Python que encontra a **rota mais barata** de um robô em uma grade
usando **recursão pura** (sem memoização), e compara com uma **regra gulosa**.

Integrantes: Leonardo Lucas Braz Araújo, Carlos Adrians Araújo Damacena e
Matheus Pinto Clemente.

## Arquivos do código

```
projeto_robo/
├── __init__.py
└── robo.py           ← resolver, recursivo, guloso, contar_chamadas, validar_custos
tests/
└── test_robo.py      ← 16 testes automáticos (casos do professor + casos do grupo)
main.py               ← demonstração pela linha de comando
pyproject.toml
README.md
```

O relatório é entregue à parte, no arquivo `entrega1_grupo06.pdf`.

## Como executar

Requer Python 3.10 ou mais novo. O código não usa nenhuma biblioteca externa.
No Windows, se o comando `python` não funcionar, use `py` no lugar.

```bash
python main.py
```

No PowerShell, as aspas dentro do JSON são escritas como `\"`:

```bash
python main.py '{\"custos\": [[1, 2], [3, 4]]}'
```

## Como testar

```bash
python -m unittest discover -s tests -v
```

O resultado esperado termina com `Ran 16 tests` e `OK`.

---

## Explicação do código (para a apresentação)

### 1. `resolver(entrada)` — a "porta de entrada"
1. Recebe um **texto** JSON, por exemplo `{"custos": [[2, 1], [3, 4]]}`.
2. Usa `json.loads` para transformar o texto em dados do Python (`null` vira `None`).
3. Valida: o texto precisa ser um objeto com a chave `custos`; `custos` precisa
   ser uma lista não vazia de linhas não vazias, todas do mesmo tamanho, e cada
   valor precisa ser inteiro positivo ou `null`. (`true`, `"1"`, `1.5`, `0` e
   `-1` são recusados.)
4. Se for inválido devolve `{"status": "entrada_invalida", "erro": "..."}`.
5. Se for válido chama `recursivo` e devolve `{"status": "ok", "custo": N}`
   ou `{"status": "sem_caminho", "custo": None}`.

### 2. `recursivo(mapa)` — a recursão
A função interna `_menor_custo(mapa, linha, coluna)` responde à pergunta:
*"qual o menor custo para ir **desta casa** até a chegada?"*

- **Obstáculo** (`None`) → impossível (`None`).
- **Chegada** → o custo da própria casa.
- **Outra casa** → toda rota daqui começa indo para a direita **ou** para baixo.
  Ela pergunta (recursivamente) o custo das duas opções que estão dentro da
  grade, fica com a menor e soma o custo da casa atual. Se nenhuma das duas
  chega, devolve `None`.

Nada é guardado entre chamadas: se duas rotas passam pela mesma casa, a casa
é calculada de novo. Por isso a quantidade de chamadas cresce muito rápido.

### 3. `contar_chamadas(mapa)` — a medição
Roda **a mesma recursão**, só que conta quantas vezes `_menor_custo` foi
chamada. O contador guarda só um número, nenhum resultado.

| Grade | 2×3 | 3×3 | 6×6 | 10×10 | 1×10 | Exemplo |
|---|---|---|---|---|---|---|
| Chamadas | 9 | 19 | 923 | 184.755 | 10 | 43 |

### 4. `guloso(mapa)` — a regra gulosa
A partir da partida, olha só os vizinhos livres (direita e baixo), anda para o
mais barato e, no empate, vai para a direita. Não olha o futuro, por isso erra:

| Grade | Guloso | Recursivo (correto) |
|---|---|---|
| Exemplo do enunciado | 26 | 11 |
| Própria 4×4 `[[1,1,1,1],[2,9,9,9],[1,9,9,9],[1,1,1,1]]` | 23 | 8 |
| Própria 3×3 `[[1,1,1],[2,9,9],[1,1,1]]` | 13 | 6 |
| Própria 3×3 `[[1,1,1],[5,1,null],[5,5,1]]` | fica preso | 9 |

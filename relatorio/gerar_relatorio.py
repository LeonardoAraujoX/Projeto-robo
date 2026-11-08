"""Gera o relatório entrega1_grupo06.pdf.

Todos os números do relatório (custos, chamadas, resultados dos testes) são
obtidos EXECUTANDO o código do projeto no momento da geração — nada é digitado
à mão. Se algum resultado mudar, o relatório muda junto.

Uso (a partir da pasta do projeto):
    pip install reportlab
    python relatorio/gerar_relatorio.py
"""

import datetime
import inspect
import io
import json
import math
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "tests"))

from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_CENTER  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table,
    TableStyle,
)

from projeto_robo import contar_chamadas, guloso, recursivo, resolver, robo  # noqa: E402
import test_robo as T  # noqa: E402

# ---------------------------------------------------------------------------
# PREENCHAM AQUI os nomes dos integrantes do grupo e rodem o script de novo.
# ---------------------------------------------------------------------------
INTEGRANTES = [
    "Nome do Integrante 1",
    "Nome do Integrante 2",
    "Nome do Integrante 3",
    "Nome do Integrante 4",
]
GRUPO = "06"
PROFESSOR = "Prof. Jemerson Damásio"

SAIDA = os.path.join(RAIZ, "entrega", f"entrega1_grupo{GRUPO}.pdf")

# ---------------------------------------------------------------------------
# Fontes (Arial/Consolas do Windows, se existirem; senão as padrão do PDF)
# ---------------------------------------------------------------------------
FONTES_WIN = "C:/Windows/Fonts"
try:
    pdfmetrics.registerFont(TTFont("Texto", os.path.join(FONTES_WIN, "arial.ttf")))
    pdfmetrics.registerFont(TTFont("Texto-B", os.path.join(FONTES_WIN, "arialbd.ttf")))
    pdfmetrics.registerFont(TTFont("Texto-I", os.path.join(FONTES_WIN, "ariali.ttf")))
    pdfmetrics.registerFont(TTFont("Codigo", os.path.join(FONTES_WIN, "consola.ttf")))
    from reportlab.lib.fonts import addMapping
    addMapping("Texto", 0, 0, "Texto")
    addMapping("Texto", 1, 0, "Texto-B")
    addMapping("Texto", 0, 1, "Texto-I")
    addMapping("Texto", 1, 1, "Texto-B")
    F, FB, FC = "Texto", "Texto-B", "Codigo"
except Exception:  # noqa: BLE001 - fora do Windows usamos as fontes padrão
    F, FB, FC = "Helvetica", "Helvetica-Bold", "Courier"

AZUL = colors.HexColor("#1F4E79")
CINZA = colors.HexColor("#F2F2F2")
OBST = colors.HexColor("#595959")

base = getSampleStyleSheet()
S = {
    "titulo": ParagraphStyle("titulo", parent=base["Title"], fontName=FB, fontSize=22,
                             textColor=AZUL, spaceAfter=10),
    "sub": ParagraphStyle("sub", parent=base["Normal"], fontName=F, fontSize=13,
                          alignment=TA_CENTER, spaceAfter=6),
    "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName=FB, fontSize=15,
                         textColor=AZUL, spaceBefore=10, spaceAfter=6),
    "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName=FB, fontSize=12,
                         textColor=AZUL, spaceBefore=8, spaceAfter=4),
    "p": ParagraphStyle("p", parent=base["Normal"], fontName=F, fontSize=10.5,
                        leading=14.5, spaceAfter=6),
    "li": ParagraphStyle("li", parent=base["Normal"], fontName=F, fontSize=10.5,
                         leading=14.5, leftIndent=14, bulletIndent=4, spaceAfter=3),
    "cel": ParagraphStyle("cel", parent=base["Normal"], fontName=F, fontSize=8.5, leading=10.5),
    "celc": ParagraphStyle("celc", parent=base["Normal"], fontName=FC, fontSize=8, leading=10),
    "code": ParagraphStyle("code", parent=base["Code"], fontName=FC, fontSize=7.6, leading=9.4,
                           backColor=CINZA, borderPadding=6, leftIndent=4, rightIndent=4,
                           spaceBefore=4, spaceAfter=10),
}


def p(texto):
    return Paragraph(texto, S["p"])


def li(texto):
    return Paragraph(texto, S["li"], bulletText="•")


def c(texto):
    """Trecho de código dentro de um parágrafo."""
    return f'<font name="{FC}">{texto}</font>'


def esc(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tabela(linhas, larguras, cabecalho=True, estilo_extra=()):
    t = Table(linhas, colWidths=larguras, repeatRows=1 if cabecalho else 0)
    estilo = [
        ("FONT", (0, 0), (-1, -1), F, 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFBFBF")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if cabecalho:
        estilo += [("BACKGROUND", (0, 0), (-1, 0), AZUL),
                   ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                   ("FONT", (0, 0), (-1, 0), FB, 9)]
    t.setStyle(TableStyle(estilo + list(estilo_extra)))
    return t


def desenhar_grade(grade, destaque=None, numeros=None, cor_destaque="#C6E0B4"):
    """Desenha a grade como tabela. `destaque` = casas a colorir.
    `numeros` (opcional) substitui o texto de cada casa."""
    destaque = destaque or set()
    dados = []
    for i, linha in enumerate(grade):
        dados.append([
            ("X" if v is None else str(v)) if numeros is None else str(numeros[i][j])
            for j, v in enumerate(linha)
        ])
    t = Table(dados, colWidths=[0.9 * cm] * len(grade[0]), rowHeights=[0.75 * cm] * len(grade))
    estilo = [
        ("FONT", (0, 0), (-1, -1), FB, 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#7F7F7F")),
    ]
    for i, linha in enumerate(grade):
        for j, v in enumerate(linha):
            if v is None:
                estilo += [("BACKGROUND", (j, i), (j, i), OBST),
                           ("TEXTCOLOR", (j, i), (j, i), colors.white)]
            elif (i, j) in destaque:
                estilo.append(("BACKGROUND", (j, i), (j, i), colors.HexColor(cor_destaque)))
    t.setStyle(TableStyle(estilo))
    return t


def lado_a_lado(*itens, legendas=()):
    linha1 = list(itens)
    linhas = [linha1]
    if legendas:
        legenda = ParagraphStyle("legenda", parent=S["cel"], alignment=TA_CENTER)
        linhas.append([Paragraph(f"<i>{x}</i>", legenda) for x in legendas])
    t = Table(linhas, hAlign="LEFT")
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10)]))
    return t


def codigo(funcao):
    return Preformatted(inspect.getsource(funcao).rstrip(), S["code"])


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont(F, 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, f"Projeto do Robô — Entrega 1 — Grupo {GRUPO}")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Execução real do código e dos testes
# ---------------------------------------------------------------------------
def rodar_testes():
    saida = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(T)
    resultado = unittest.TextTestRunner(stream=saida, verbosity=2).run(suite)
    return resultado, saida.getvalue()


def formatar_resultado(r):
    return json.dumps(r, ensure_ascii=False)


def montar():
    resultado_testes, log_testes = rodar_testes()
    ok_testes = resultado_testes.wasSuccessful()
    total_testes = resultado_testes.testsRun
    falhas = len(resultado_testes.failures) + len(resultado_testes.errors)

    ex = T.GRADE_EXEMPLO
    custo_ex, chamadas_ex = contar_chamadas(ex)
    guloso_ex = guloso(ex)
    g_erra, g_presa = T.GRADE_GULOSA_ERRA, T.GRADE_GULOSA_PRESA

    # Chamadas por casa na grade do exemplo (contadas à mão pelo grupo; a soma
    # é conferida com a medição real logo abaixo).
    chamadas_por_casa = [[1, 1, 1, 1, 1],
                         [1, 2, 1, 2, 3],
                         [1, 1, 2, 4, 3],
                         [1, 2, 4, 4, 7]]
    assert sum(map(sum, chamadas_por_casa)) == chamadas_ex, "tabela de chamadas por casa errada"

    hist = []

    # ------------------------------------------------------------------ capa
    hist += [Spacer(1, 3.5 * cm),
             Paragraph("Projeto do Robô", S["titulo"]),
             Paragraph("Entrega 1 — Rota de menor custo com recursão", S["sub"]),
             Spacer(1, 0.6 * cm),
             Paragraph(f"<b>Grupo {GRUPO}</b>", S["sub"]),
             Paragraph(PROFESSOR, S["sub"]),
             Paragraph("Linguagem: Python 3", S["sub"]),
             Spacer(1, 1.2 * cm),
             Paragraph("<b>Integrantes</b>", S["sub"])]
    hist += [Paragraph(nome, S["sub"]) for nome in INTEGRANTES]
    hist += [Spacer(1, 1.5 * cm),
             Paragraph(datetime.date.today().strftime("%d/%m/%Y"), S["sub"]),
             PageBreak()]

    # --------------------------------------------------------------- sumário
    hist += [Paragraph("Sumário", S["h1"])]
    for item in ["1. Descrição do problema", "2. Solução recursiva",
                 "3. Testes", "4. Por que funciona", "5. Medição do trabalho",
                 "6. Regra gulosa", "7. Conferência com os critérios de avaliação",
                 "Apêndice — Como executar e arquivos entregues"]:
        hist.append(li(item))
    hist.append(Spacer(1, 0.4 * cm))
    hist.append(p("Todos os números deste relatório foram obtidos executando o código "
                  "entregue (o relatório é gerado pelo script "
                  f"{c('relatorio/gerar_relatorio.py')}, que chama as funções do projeto "
                  "e roda os testes automáticos no momento da geração)."))
    hist.append(PageBreak())

    # ----------------------------------------------------------- 1. problema
    hist += [Paragraph("1. Descrição do problema", S["h1"]),
             p("Um robô está no <b>canto superior esquerdo</b> de uma grade retangular e "
               "precisa chegar ao <b>canto inferior direito</b>. Cada casa tem um custo de "
               "energia. O objetivo é encontrar o <b>menor custo total</b> possível para "
               "fazer esse trajeto, ou informar que o trajeto é impossível."),
             Paragraph("Regras", S["h2"]),
             li("O robô anda <b>uma casa por vez</b>, e só para a <b>direita</b> ou para "
                "<b>baixo</b>."),
             li("Ele <b>não sai da grade</b> e <b>não entra em obstáculos</b> (casas "
                f"marcadas com X, representadas por {c('null')} no JSON)."),
             li("O custo de uma rota é a <b>soma de todas as casas visitadas</b>, "
                "incluindo a casa de partida e a de chegada."),
             li("Se a partida ou a chegada forem obstáculos, ou se os obstáculos "
                "bloquearem todas as rotas, não existe caminho."),
             Paragraph("Entrada", S["h2"]),
             p(f"A entrada é um <b>texto</b> no formato JSON com a chave {c('custos')}, "
               "que contém a grade como uma lista de linhas. Exemplo (a grade do enunciado):"),
             Preformatted('{"custos": [[2, 1, 9, 9, 9],\n'
                          '            [3, null, 1, 1, 9],\n'
                          '            [1, 1, 1, null, 2],\n'
                          '            [9, 9, 1, 1, 1]]}', S["code"]),
             p("A entrada é <b>válida</b> somente quando:"),
             li("o texto é um JSON bem formado e é um <b>objeto</b> com a chave "
                f"{c('custos')} (outras chaves são ignoradas);"),
             li(f"{c('custos')} é uma <b>lista não vazia</b> de linhas;"),
             li("cada linha é uma <b>lista não vazia</b> e todas as linhas têm o "
                "<b>mesmo tamanho</b>;"),
             li(f"cada valor é um <b>inteiro positivo</b> (1, 2, 3, ...) ou {c('null')}. "
                f"Não valem {c('true')}/{c('false')}, textos como {c('&quot;1&quot;')}, "
                f"números com casas decimais como {c('1.5')}, zero ou negativos."),
             Paragraph("Saída", S["h2"]),
             p(f"A função {c('resolver(entrada)')} devolve um dicionário Python com um destes "
               "formatos:"),
             tabela([["Situação", "Saída"],
                     ["Existe rota", '{"status": "ok", "custo": 11}'],
                     ["Entrada válida, sem rota", '{"status": "sem_caminho", "custo": null}'],
                     ["Entrada inválida", '{"status": "entrada_invalida", "erro": "mensagem"}']],
                    [5 * cm, 10 * cm],
                    estilo_extra=[("FONT", (1, 1), (1, -1), FC, 8.5)]),
             Spacer(1, 6),
             p(f"Em Python o {c('null')} aparece como {c('None')}. O campo "
               f"{c('caminho')} (lista de coordenadas) não é incluído, pois só será exigido "
               "na Entrega 2."),
             ]

    # exemplos próprios
    ex_sem_rota = [[3, 2, None], [4, None, 5], [None, 6, 1]]
    txt_sem_rota = '{"custos": [[3, 2, null], [4, null, 5], [null, 6, 1]]}'
    txt_invalida = '{"custos": "1 2 3"}'
    r_sem_rota = resolver(txt_sem_rota)
    r_invalida = resolver(txt_invalida)
    hist += [Paragraph("Exemplos próprios do grupo", S["h2"]),
             p("<b>a) Entrada válida sem rota.</b> Todos os valores são inteiros positivos "
               "ou null e as linhas têm o mesmo tamanho, então a entrada é válida. Porém, "
               "da partida (3) o robô só pode ir para o 2 (direita) ou para o 4 (baixo). "
               "Do 2, a direita e a casa de baixo são obstáculos; do 4, a casa de baixo e "
               "a da direita também são. O robô fica cercado e nunca chega ao 1 da chegada."),
             KeepTogether([desenhar_grade(ex_sem_rota),
                           Spacer(1, 4),
                           Preformatted(f"Entrada: {txt_sem_rota}\n"
                                        f"Saída:   {formatar_resultado(r_sem_rota)}", S["code"])]),
             p(f"<b>b) Entrada inválida.</b> A chave {c('custos')} existe, mas o seu valor é um "
               "texto e não uma lista de linhas. Por isso a grade não pode ser montada e o "
               "programa recusa a entrada, explicando o motivo:"),
             Preformatted(f"Entrada: {txt_invalida}\n"
                          f"Saída:   {formatar_resultado(r_invalida)}", S["code"]),
             PageBreak()]

    # --------------------------------------------------------- 2. recursão
    hist += [Paragraph("2. Solução recursiva", S["h1"]),
             p("A ideia central é responder, para uma casa qualquer, à pergunta: "
               "<i>“qual é o menor custo para ir desta casa até a chegada?”</i>. "
               f"A função interna {c('_menor_custo(mapa, linha, coluna, contador)')} faz isso:"),
             li("<b>Obstáculo</b> → devolve None (impossível)."),
             li("<b>Chegada</b> → devolve o custo da própria casa."),
             li("<b>Qualquer outra casa</b> → toda rota que sai daqui começa indo para a "
                "direita ou para baixo. A função chama a si mesma para as duas opções "
                "(somente as que estão dentro da grade; posições fora da grade contam como "
                "impossíveis e nem são chamadas), escolhe a menor resposta válida e soma o "
                "custo da casa atual. Se nenhuma das duas chega, devolve None."),
             p(f"{c('recursivo(mapa)')} apenas começa a recursão na partida (0, 0). "
               f"<b>Não há memoização</b>: nada é guardado entre chamadas — se duas rotas "
               "passam pela mesma casa, a casa é calculada de novo. O objeto "
               f"{c('Contador')} guarda só <i>quantas</i> chamadas aconteceram (usado na "
               "tarefa 5), nunca um resultado."),
             codigo(robo._menor_custo),
             codigo(robo.recursivo),
             codigo(robo.contar_chamadas),
             Paragraph("Validação e função de contrato", S["h2"]),
             p(f"{c('resolver(entrada)')} lê o texto com o leitor de JSON da linguagem "
               f"({c('json.loads')}), confere as regras de validade com "
               f"{c('validar_custos')} e só então chama {c('recursivo')}. Observação: em "
               f"Python {c('True')} também é do tipo {c('int')}; por isso o código recusa "
               f"{c('bool')} explicitamente."),
             codigo(robo.validar_custos),
             codigo(robo.resolver),
             PageBreak()]

    # ------------------------------------------------------------ 3. testes
    hist += [Paragraph("3. Testes", S["h1"]),
             p(f"Os testes ficam em {c('tests/test_robo.py')}, usam o módulo "
               f"{c('unittest')} (já vem com o Python) e rodam sozinhos com o comando "
               f"{c('python -m unittest discover -s tests -v')}. Cada caso compara a "
               "saída de resolver com o resultado esperado; nos casos de entrada inválida "
               f"o teste confere o status e se há uma mensagem em {c('erro')}."),
             p(f"<b>Resultado da execução no momento da geração deste relatório:</b> "
               f"{total_testes} testes executados, {falhas} falhas — "
               f"<b>{'TODOS PASSARAM (OK)' if ok_testes else 'HOUVE FALHAS'}</b>.")]

    def linhas_casos(casos):
        linhas = [["Entrada", "Esperado", "Obtido", ""]]
        for descricao, entrada, status, custo in casos:
            r = resolver(entrada)
            esperado = f"{status}, custo {custo}" if status == "ok" else status
            obtido = f"{r['status']}, custo {r['custo']}" if r["status"] == "ok" else r["status"]
            passou = (r == {"status": status, "custo": custo}) if status != "entrada_invalida" \
                else (r["status"] == status and bool(r.get("erro")))
            linhas.append([Paragraph(esc(descricao), S["celc"]),
                           Paragraph(esc(esperado), S["cel"]),
                           Paragraph(esc(obtido), S["cel"]),
                           "OK" if passou else "FALHOU"])
        return linhas

    verde = [("TEXTCOLOR", (3, 1), (3, -1), colors.HexColor("#2E7D32")),
             ("FONT", (3, 1), (3, -1), FB, 9), ("ALIGN", (3, 0), (3, -1), "CENTER")]
    larg = [7.6 * cm, 3.6 * cm, 3.6 * cm, 1.6 * cm]
    hist += [Paragraph("3.1 Casos exigidos pelo professor", S["h2"]),
             tabela(linhas_casos(T.CASOS_PROFESSOR), larg, estilo_extra=verde),
             Paragraph("3.2 Casos criados pelo grupo", S["h2"]),
             tabela(linhas_casos(T.CASOS_GRUPO), larg, estilo_extra=verde),
             Spacer(1, 6),
             Paragraph("3.3 Outros testes automáticos", S["h2"]),
             li("contagem de chamadas nas grades 2×3, 3×3, 6×6, 10×10 e 1×10 e na grade do "
                "exemplo (tarefa 5);"),
             li("regra gulosa: 26 contra 11 na grade do exemplo, grade própria em que ela "
                "erra, grade própria em que ela fica presa, empate preferindo a direita, "
                "partida bloqueada e grade de uma casa (tarefa 6);"),
             li("recursivo não altera a grade recebida; saída não tem o campo caminho; "
                "entrada que não é texto é recusada."),
             Paragraph("3.4 Saída do executor de testes", S["h2"]),
             Preformatted(esc(log_testes.strip()), ParagraphStyle(
                 "log", parent=S["code"], fontSize=6.6, leading=8)),
             PageBreak()]

    # ------------------------------------------------------ 4. por que funciona
    hist += [Paragraph("4. Por que funciona", S["h1"]),
             Paragraph("Por que a recursão sempre termina?", S["h2"]),
             p("De uma casa (linha, coluna) até a chegada faltam exatamente "
               "(última linha − linha) + (última coluna − coluna) movimentos. Cada chamada "
               "recursiva anda uma casa para a direita ou para baixo, então <b>a cada chamada "
               "falta um movimento a menos</b>. Esse número nunca fica negativo, porque só "
               "chamamos vizinhos que estão dentro da grade. Logo, depois de no máximo "
               "linhas + colunas − 2 chamadas encadeadas, chega-se à chegada (caso base) ou a "
               "um obstáculo (outro caso base), e a recursão para. Na pior das hipóteses a "
               "profundidade é linhas + colunas − 1."),
             Paragraph("Por que ela encontra o menor custo?", S["h2"]),
             p("Toda rota que sai de uma casa (que não é a chegada) <b>começa indo para a "
               "direita ou para baixo</b> — não há outra opção. Então o menor custo a partir "
               "dela é o custo da casa mais o menor entre: o melhor custo a partir da casa da "
               "direita e o melhor custo a partir da casa de baixo. Supondo que as chamadas "
               "para os vizinhos (que estão mais perto da chegada) já devolvem o menor custo "
               "correto, escolher o menor dos dois dá o menor custo correto para a casa atual. "
               "Como o caso base (chegada = custo da própria casa) está certo, por indução a "
               "resposta está certa em todas as casas, inclusive na partida. Em outras "
               "palavras: a recursão examina, de forma implícita, <b>todas</b> as rotas "
               "possíveis e fica com a mais barata."),
             Paragraph("O que acontece quando não há rota?", S["h2"]),
             p("Obstáculos devolvem None, e posições fora da grade nunca são escolhidas. "
               "Uma casa só devolve um número quando pelo menos um dos vizinhos devolveu um "
               "número; se os dois devolveram None (ou não existem), ela também devolve None. "
               "Assim o None “sobe” até a partida exatamente quando nenhuma rota consegue "
               f"chegar. {c('resolver')} transforma esse None em "
               f"{c('{&quot;status&quot;: &quot;sem_caminho&quot;, &quot;custo&quot;: null}')}. "
               "Exemplos: [[null]] (partida bloqueada), [[1, 1], [1, null]] (chegada "
               "bloqueada) e [[1, null], [null, 1]] (obstáculos no meio)."),
             PageBreak()]

    # ----------------------------------------------------------- 5. medição
    linhas_med = [["Grade (casas = 1)", "Enunciado", "Medido", "C(L+C, L) − 1", "Confere?"]]
    for L, C_, esperado in T.MEDICOES_PROFESSOR:
        custo, chamadas = contar_chamadas(T.grade_de_uns(L, C_))
        formula = math.comb(L + C_, L) - 1
        linhas_med.append([f"{L} × {C_}", f"{esperado:,}".replace(",", "."),
                           f"{chamadas:,}".replace(",", "."), f"{formula:,}".replace(",", "."),
                           "sim" if chamadas == esperado == formula else "NÃO"])
    linhas_med.append(["Grade do exemplo (4 × 5)", "—", str(chamadas_ex),
                       f"{math.comb(9, 4) - 1} sem obstáculos", "—"])
    canto_10 = math.comb(18, 9)

    hist += [Paragraph("5. Medição do trabalho", S["h1"]),
             p(f"Usamos {c('contar_chamadas(mapa)')}, que executa <b>exatamente a mesma "
               "recursão</b> e conta quantas vezes a função foi chamada (incluindo a "
               "primeira chamada, na partida). Como o programa só chama vizinhos que estão "
               "dentro da grade, os números batem com a tabela do enunciado:"),
             tabela(linhas_med, [4.4 * cm, 3.2 * cm, 2.2 * cm, 3.6 * cm, 2 * cm],
                    estilo_extra=[("ALIGN", (1, 0), (-1, -1), "CENTER")]),
             Spacer(1, 6),
             Paragraph("Explicação dos números", S["h2"]),
             p("Sem memoização, a função é chamada em uma casa <b>uma vez para cada rota "
               "diferente que leva da partida até ela</b>. Até a casa (i, j) existem "
               "C(i + j, i) rotas (escolher quais dos i + j passos são para baixo). Somando "
               "em todas as casas de uma grade L × C, o total de chamadas é "
               "<b>C(L + C, L) − 1</b>, coluna que calculamos acima e que coincide com a medição."),
             li("<b>1 × 10</b>: só existe uma rota, então cada casa é chamada uma única vez: "
                "10 chamadas."),
             li("<b>2 × 3</b>: as casas recebem 1, 1, 1 / 1, 2, 3 chamadas = 9."),
             li(f"<b>10 × 10</b>: 184.755 chamadas para uma grade de apenas 100 casas. Só a "
                f"casa de chegada é chamada C(18, 9) = {canto_10:,} vezes".replace(",", ".")
                + ". O trabalho cresce de forma exponencial, porque o mesmo pedaço da grade é "
                  "recalculado muitas vezes. (Guardar esses resultados seria a memoização, "
                  "que fica para a Entrega 2.)"),
             Paragraph("Grade do exemplo", S["h2"]),
             p(f"Na grade do exemplo foram medidas <b>{chamadas_ex} chamadas</b> (custo "
               f"{custo_ex}). Sem obstáculos, uma grade 4 × 5 teria {math.comb(9, 4) - 1}. "
               "A diferença acontece porque os dois obstáculos também recebem chamadas, mas "
               "param imediatamente (caso base) e não geram chamadas para a frente; todas as "
               "rotas que passariam por eles são cortadas. A tabela abaixo mostra quantas vezes "
               "cada casa foi chamada (obstáculos em cinza). A soma é "
               f"{sum(map(sum, chamadas_por_casa))}, igual à medição, e as 7 chamadas na "
               "chegada correspondem às 7 rotas que existem nessa grade."),
             lado_a_lado(desenhar_grade(ex), desenhar_grade(ex, numeros=chamadas_por_casa),
                         legendas=("Custos", "Chamadas por casa")),
             PageBreak()]

    # ------------------------------------------------------------ 6. guloso
    caminho_guloso_ex = {(0, 0), (0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)}
    caminho_otimo_ex = {(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (3, 3), (3, 4)}
    caminho_guloso_erra = {(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)}
    caminho_otimo_erra = {(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)}
    caminho_guloso_presa = {(0, 0), (0, 1), (0, 2)}
    caminho_otimo_presa = {(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)}

    hist += [Paragraph("6. Regra gulosa", S["h1"]),
             p(f"{c('guloso(mapa)')} começa na partida e, a cada passo, olha apenas os vizinhos "
               "<b>livres</b> (direita e baixo, dentro da grade e sem obstáculo) e anda para o "
               "<b>mais barato</b>. No <b>empate prefere a direita</b> (comparação "
               f"{c('direita &lt;= baixo')}). Se não houver vizinho livre antes da chegada, o "
               "robô fica preso e a função devolve None. Ela nunca volta atrás nem olha o "
               "futuro — por isso pode errar."),
             codigo(robo.guloso),
             Paragraph("6.1 Grade do exemplo: 26 contra 11", S["h2"]),
             p(f"Resultado medido: <b>guloso = {guloso_ex}</b>, <b>recursivo = {custo_ex}</b>."),
             lado_a_lado(desenhar_grade(ex, caminho_guloso_ex, cor_destaque="#F8CBAD"),
                         desenhar_grade(ex, caminho_otimo_ex),
                         legendas=(f"Rota gulosa: 2+1+9+1+1+9+2+1 = {guloso_ex}",
                                   f"Rota ótima: 2+3+1+1+1+1+1+1 = {custo_ex}")),
             p("Onde a escolha atrapalhou: logo no primeiro passo o guloso compara 1 (direita) "
               "com 3 (baixo) e vai para a direita. Parece mais barato, mas leva à linha de "
               "cima, onde a casa de baixo do 1 é obstáculo e a única saída é um 9. Depois, na "
               "casa (1, 2), há empate entre 1 (direita) e 1 (baixo); a preferência pela "
               "direita leva a outro 9. A rota ótima aceita pagar 3 no início para descer pela "
               "primeira coluna e seguir só por casas de custo 1."),
             PageBreak(),
             Paragraph("6.2 Grade própria (3 × 3) em que o guloso erra", S["h2"]),
             Preformatted('{"custos": [[1, 1, 1],\n            [2, 9, 9],\n'
                          '            [1, 1, 1]]}', S["code"]),
             p(f"Resultado medido: <b>guloso = {guloso(g_erra)}</b>, "
               f"<b>recursivo = {recursivo(g_erra)}</b>."),
             lado_a_lado(desenhar_grade(g_erra, caminho_guloso_erra, cor_destaque="#F8CBAD"),
                         desenhar_grade(g_erra, caminho_otimo_erra),
                         legendas=(f"Rota gulosa: 1+1+1+9+1 = {guloso(g_erra)}",
                                   f"Rota ótima: 1+2+1+1+1 = {recursivo(g_erra)}")),
             p("Onde a escolha atrapalhou: na partida o guloso compara 1 (direita) com 2 "
               "(baixo) e vai para a direita para “economizar” 1. Ao fazer isso, ele fica do "
               "lado de cima de uma parede de 9s: toda rota que começa pela direita precisa "
               "atravessar a linha do meio por um 9. Quem desce primeiro paga 2, mas passa pela "
               "única casa barata da linha do meio e termina em 6. Uma economia de 1 no início "
               "custou 7 a mais no total."),
             Paragraph("6.3 Grade própria (3 × 3) em que o guloso fica preso", S["h2"]),
             Preformatted('{"custos": [[1, 1, 1],\n            [5, 1, null],\n'
                          '            [5, 5, 1]]}', S["code"]),
             p(f"Resultado medido: <b>guloso = "
               f"{'sem caminho (não chega)' if guloso(g_presa) is None else guloso(g_presa)}</b>, "
               f"<b>recursivo = {recursivo(g_presa)}</b>."),
             lado_a_lado(desenhar_grade(g_presa, caminho_guloso_presa, cor_destaque="#F8CBAD"),
                         desenhar_grade(g_presa, caminho_otimo_presa),
                         legendas=("Rota gulosa: fica presa no canto (0, 2)",
                                   f"Rota ótima: 1+1+1+5+1 = {recursivo(g_presa)}")),
             p("Onde a escolha atrapalhou: na casa (0, 1) há empate entre 1 (direita) e 1 "
               "(baixo). A regra prefere a direita e vai para o canto (0, 2), onde a direita "
               "sai da grade e a casa de baixo é obstáculo: o robô fica preso, mesmo existindo "
               "uma rota de custo 9. A regra gulosa nem sempre encontra uma rota."),
             PageBreak()]

    # ------------------------------------------------------- 7. critérios
    crit = [
        ["Critério (pontos)", "Onde está atendido"],
        ["Descrição do problema (0,5)",
         "Seção 1: entrada, saída, objetivo, regras e regras de validade; exemplo próprio "
         "de entrada válida sem rota e de entrada inválida, com a saída real do programa."],
        ["Recursão e testes (1,0)",
         f"Seção 2: recursivo sem memoização; Seção 3: {len(T.CASOS_PROFESSOR)} casos do "
         f"professor e {len(T.CASOS_GRUPO)} casos do grupo; {total_testes} testes automáticos, "
         f"{'todos passando' if ok_testes else 'COM FALHAS'}."],
        ["Por que funciona (0,6)",
         "Seção 4: por que termina (falta um movimento a menos), por que acerta (toda rota "
         "começa pela direita ou por baixo + indução) e como detecta a falta de rota."],
        ["Medição do trabalho (0,6)",
         "Seção 5: chamadas medidas 9, 19, 923, 184.755, 10 (iguais ao enunciado) e "
         f"{chamadas_ex} na grade do exemplo, com fórmula e explicação por casa."],
        ["Regra gulosa (0,3)",
         f"Seção 6: guloso com empate para a direita; {guloso_ex} contra {custo_ex} no exemplo; "
         "grade própria 3 × 3 com custos (13 contra 6) e explicação de onde errou; extra: "
         "grade em que fica preso."],
    ]
    hist += [Paragraph("7. Conferência com os critérios de avaliação", S["h1"]),
             tabela([[Paragraph(f"<b>{a}</b>", S["cel"]), Paragraph(b, S["cel"])]
                     if i else [a, b] for i, (a, b) in enumerate(crit)],
                    [4.5 * cm, 11.5 * cm]),
             Spacer(1, 10),
             p("<b>Fora do escopo desta entrega (de propósito):</b> memoização, tabela de "
               f"resultados e o campo {c('caminho')} com a lista de coordenadas, que ficam "
               "para a Entrega 2."),
             ]

    # ---------------------------------------------------------------- apêndice
    hist += [Paragraph("Apêndice — Como executar e arquivos entregues", S["h1"]),
             p("Requer Python 3.10 ou mais novo; o código e os testes não usam bibliotecas "
               "externas (a biblioteca reportlab é usada só para gerar este PDF)."),
             Preformatted("python main.py                               # demonstração\n"
                          "python main.py \"{\\\"custos\\\": [[1, 2], [3, 4]]}\"\n"
                          "python -m unittest discover -s tests -v     # testes\n"
                          "python relatorio/gerar_relatorio.py         # gera este PDF\n"
                          "python empacotar.py                         # gera o .zip", S["code"]),
             tabela([["Arquivo", "Conteúdo"],
                     ["projeto_robo/robo.py", "resolver, recursivo, guloso, contar_chamadas, validar_custos"],
                     ["tests/test_robo.py", "testes automáticos (unittest)"],
                     ["main.py", "demonstração pela linha de comando"],
                     ["relatorio/gerar_relatorio.py", "gera este relatório executando o código"],
                     ["empacotar.py", f"gera entrega/entrega1_grupo{GRUPO}.zip"],
                     ["README.md", "instruções e explicação do código para a apresentação"]],
                    [5.5 * cm, 10.5 * cm],
                    estilo_extra=[("FONT", (0, 1), (0, -1), FC, 8.5)]),
             ]

    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    doc = SimpleDocTemplate(SAIDA, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            title=f"Projeto do Robô — Entrega 1 — Grupo {GRUPO}",
                            author=f"Grupo {GRUPO}")
    doc.build(hist, onFirstPage=lambda cv, d: None, onLaterPages=rodape)
    return ok_testes, total_testes


if __name__ == "__main__":
    ok, total = montar()
    print(f"Relatório gerado em: {SAIDA}")
    print(f"Testes: {total} executados — {'OK' if ok else 'FALHAS'}")
    sys.exit(0 if ok else 1)

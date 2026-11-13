"""Monta entrega/entrega1_grupo06.zip só com o código e os testes.

O relatório (entrega/entrega1_grupo06.pdf) é entregue à parte.

Uso (a partir da pasta do projeto):
    python empacotar.py
"""

import os
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
GRUPO = "06"
DESTINO = os.path.join(RAIZ, "entrega", f"entrega1_grupo{GRUPO}.zip")

ARQUIVOS = [
    "README.md",
    "main.py",
    "pyproject.toml",
    "projeto_robo/__init__.py",
    "projeto_robo/robo.py",
    "tests/test_robo.py",
]


def main():
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    pasta = f"entrega1_grupo{GRUPO}"
    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED) as zipado:
        for relativo in ARQUIVOS:
            caminho = os.path.join(RAIZ, relativo)
            if not os.path.exists(caminho):
                raise SystemExit(f"Arquivo não encontrado: {relativo}")
            zipado.write(caminho, f"{pasta}/{relativo}")
    print(f"Pacote gerado em: {DESTINO}")


if __name__ == "__main__":
    main()

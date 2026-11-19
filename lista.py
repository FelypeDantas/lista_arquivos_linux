
import os
import json
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ==================================================
# CONFIGURAÇÕES
# ==================================================

CAMINHO_INICIAL = Path.home()
PROFUNDIDADE_MAX = 2
TAMANHO_GRANDE = 100 * 1024 * 1024
TAMANHO_BLOCO = 1024 * 1024

PASTAS_IGNORADAS = {
    "$RECYCLE.BIN",
    "System Volume Information",
    "__pycache__",
    ".git",
    "node_modules"
}

# ==================================================
# UTILIDADES
# ==================================================

def tamanho_legivel(tamanho):
    unidades = ["B", "KB", "MB", "GB", "TB", "PB"]

    for unidade in unidades:
        if tamanho < 1024:
            return f"{tamanho:.2f} {unidade}"
        tamanho /= 1024

    return f"{tamanho:.2f} EB"


def calcular_hash(caminho):
    """Calcula o SHA-256 de um arquivo em blocos."""

    hash_obj = hashlib.sha256()

    try:
        with open(caminho, "rb") as arquivo:
            for bloco in iter(
                lambda: arquivo.read(TAMANHO_BLOCO), b""
            ):
                hash_obj.update(bloco)

        return hash_obj.hexdigest()

    except (OSError, PermissionError):
        return None


def obter_tamanho(caminho):
    try:
        return caminho.stat(follow_symlinks=False).st_size
    except OSError:
        return None


# ==================================================
# ÁRVORE DE DIRETÓRIOS
# ==================================================

def mostrar_arvore(caminho, profundidade=PROFUNDIDADE_MAX):
    caminho = Path(caminho)

    print(f"\n📁 {caminho}")

    def percorrer(diretorio, prefixo="", nivel=0):

        if nivel >= profundidade:
            return

        try:
            entradas = sorted(
                diretorio.iterdir(),
                key=lambda item: (
                    not item.is_dir(),
                    item.name.lower()
                )
            )

        except OSError:
            print(prefixo + "└── 🔒 Acesso negado")
            return

        entradas = [
            item for item in entradas
            if item.name not in PASTAS_IGNORADAS
        ]

        for indice, entrada in enumerate(entradas):

            ultimo = indice == len(entradas) - 1

            conector = "└── " if ultimo else "├── "
            novo_prefixo = prefixo + (
                "    " if ultimo else "│   "
            )

            try:
                if entrada.is_symlink():
                    print(prefixo + conector + "🔗 " + entrada.name)

                elif entrada.is_dir():
                    print(prefixo + conector + "📁 " + entrada.name)
                    percorrer(
                        entrada,
                        novo_prefixo,
                        nivel + 1
                    )

                else:
                    print(prefixo + conector + "📄 " + entrada.name)

            except OSError:
                print(prefixo + conector + "⚠️ Erro de leitura")

    percorrer(caminho)


# ==================================================
# ESCANEAMENTO
# ==================================================

def escanear(caminho, tamanho_minimo=TAMANHO_GRANDE):

    arquivos_por_tamanho = defaultdict(list)
    arquivos_grandes = []

    total_arquivos = 0
    espaco_total = 0
    erros = 0

    print("🔎 Iniciando varredura...\n")

    for raiz, diretorios, arquivos in os.walk(
        caminho,
        topdown=True,
        followlinks=False,
        onerror=lambda erro: None
    ):

        diretorios[:] = [
            d for d in diretorios
            if d not in PASTAS_IGNORADAS
            and not (Path(raiz) / d).is_symlink()
        ]

        for nome in arquivos:

            arquivo = Path(raiz) / nome

            try:
                if arquivo.is_symlink():
                    continue

                tamanho = arquivo.stat(
                    follow_symlinks=False
                ).st_size

                total_arquivos += 1
                espaco_total += tamanho

                if tamanho >= tamanho_minimo:
                    arquivos_grandes.append(
                        (arquivo, tamanho)
                    )

                # Agrupamento por tamanho:
                # evita calcular hashes desnecessários.
                arquivos_por_tamanho[tamanho].append(arquivo)

            except OSError:
                erros += 1
                continue

    # ==================================================
    # IDENTIFICAÇÃO DE DUPLICADOS
    # ==================================================

    duplicados = []

    for tamanho, arquivos in arquivos_por_tamanho.items():

        if len(arquivos) < 2:
            continue

        hashes = defaultdict(list)

        for arquivo in arquivos:

            resultado = calcular_hash(arquivo)

            if resultado:
                hashes[resultado].append(str(arquivo))
            else:
                erros += 1

        for hash_valor, grupo in hashes.items():

            if len(grupo) > 1:
                duplicados.append({
                    "hash": hash_valor,
                    "tamanho": tamanho,
                    "arquivos": grupo,
                    "espaco_recuperavel": tamanho * (len(grupo) - 1)
                })

    arquivos_grandes.sort(
        key=lambda item: item[1],
        reverse=True
    )

    duplicados.sort(
        key=lambda item: item["espaco_recuperavel"],
        reverse=True
    )

    return {
        "total_arquivos": total_arquivos,
        "espaco_total": espaco_total,
        "arquivos_grandes": arquivos_grandes,
        "duplicados": duplicados,
        "erros": erros
    }


# ==================================================
# RELATÓRIO
# ==================================================

def relatorio(dados):

    print("\n" + "=" * 55)
    print("             📊 RELATÓRIO DE ARMAZENAMENTO")
    print("=" * 55)

    print(f"\n📄 Arquivos analisados: {dados['total_arquivos']}")
    print(f"💾 Espaço ocupado: {tamanho_legivel(dados['espaco_total'])}")
    print(f"⚠️ Erros de leitura: {dados['erros']}")

    print("\n" + "-" * 55)
    print("🪨 ARQUIVOS GRANDES")
    print("-" * 55)

    if not dados["arquivos_grandes"]:
        print("Nenhum arquivo grande encontrado.")

    for arquivo, tamanho in dados["arquivos_grandes"]:
        print(f"{tamanho_legivel(tamanho):>12} | {arquivo}")

    print("\n" + "-" * 55)
    print("🧬 ARQUIVOS DUPLICADOS")
    print("-" * 55)

    if not dados["duplicados"]:
        print("Nenhum duplicado encontrado.")

    for grupo in dados["duplicados"]:

        print(f"\nHash: {grupo['hash']}")
        print(f"Tamanho: {tamanho_legivel(grupo['tamanho'])}")
        print(
            "Espaço potencialmente recuperável:",
            tamanho_legivel(grupo["espaco_recuperavel"])
        )

        for arquivo in grupo["arquivos"]:
            print(f"   📄 {arquivo}")

    espaco_recuperavel = sum(
        grupo["espaco_recuperavel"]
        for grupo in dados["duplicados"]
    )

    print("\n" + "=" * 55)
    print(
        "💡 Espaço potencialmente recuperável:",
        tamanho_legivel(espaco_recuperavel)
    )
    print("=" * 55)


# ==================================================
# EXPORTAÇÃO JSON
# ==================================================

def exportar_json(dados, destino="relatorio_armazenamento.json"):

    resultado = {
        "data": datetime.now().isoformat(),
        "total_arquivos": dados["total_arquivos"],
        "espaco_total": dados["espaco_total"],
        "erros": dados["erros"],

        "arquivos_grandes": [
            {
                "caminho": str(arquivo),
                "tamanho": tamanho
            }
            for arquivo, tamanho in dados["arquivos_grandes"]
        ],

        "duplicados": dados["duplicados"]
    }

    try:
        with open(destino, "w", encoding="utf-8") as arquivo:
            json.dump(
                resultado,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

        print(f"\n✅ Relatório salvo em: {destino}")

    except OSError as erro:
        print(f"\n❌ Erro ao salvar relatório: {erro}")


# ==================================================
# EXECUÇÃO
# ==================================================

def main():

    parser = argparse.ArgumentParser(
        description="Analisador inteligente de armazenamento."
    )

    parser.add_argument(
        "--caminho",
        default=str(CAMINHO_INICIAL),
        help="Diretório que será analisado."
    )

    parser.add_argument(
        "--profundidade",
        type=int,
        default=PROFUNDIDADE_MAX
    )

    parser.add_argument(
        "--limite",
        type=int,
        default=TAMANHO_GRANDE // (1024 * 1024),
        help="Tamanho mínimo de arquivos grandes em MB."
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Exportar relatório JSON."
    )

    args = parser.parse_args()

    caminho = Path(args.caminho).expanduser().resolve()

    if not caminho.exists() or not caminho.is_dir():
        print("❌ Diretório inválido.")
        return

    print("\n🌳 ESTRUTURA DE DIRETÓRIOS")
    mostrar_arvore(caminho, max(0, args.profundidade))

    dados = escanear(
        caminho,
        max(0, args.limite) * 1024 * 1024
    )

    relatorio(dados)

    if args.json:
        exportar_json(dados)


if __name__ == "__main__":
    main()

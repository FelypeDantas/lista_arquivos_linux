import os
import hashlib

# ----------------------------
# CONFIGURAÇÕES
# ----------------------------

CAMINHO_INICIAL = "/"
PROFUNDIDADE_MAX = 2
TAMANHO_GRANDE = 100 * 1024 * 1024  # 100MB

# ----------------------------
# UTILIDADES
# ----------------------------

def tamanho_legivel(bytes_size):
    for unidade in ['B','KB','MB','GB','TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f}{unidade}"
        bytes_size /= 1024


def calcular_hash(caminho):
    hash_md5 = hashlib.md5()
    try:
        with open(caminho, "rb") as f:
            for bloco in iter(lambda: f.read(4096), b""):
                hash_md5.update(bloco)
        return hash_md5.hexdigest()
    except:
        return None


# ----------------------------
# ÁRVORE DE DIRETÓRIOS
# ----------------------------

def mostrar_arvore(caminho, prefixo="", nivel=0):
    if nivel > PROFUNDIDADE_MAX:
        return

    try:
        entradas = list(os.scandir(caminho))
    except PermissionError:
        print(prefixo + "🔒 acesso negado")
        return

    entradas.sort(key=lambda e: (not e.is_dir(), e.name))

    for i, entrada in enumerate(entradas):
        conector = "└── " if i == len(entradas)-1 else "├── "

        if entrada.is_dir():
            print(prefixo + conector + "📁 " + entrada.name)
            novo_prefixo = prefixo + ("    " if i == len(entradas)-1 else "│   ")
            mostrar_arvore(entrada.path, novo_prefixo, nivel+1)

        else:
            print(prefixo + conector + "📄 " + entrada.name)


# ----------------------------
# SCAN DE ARQUIVOS
# ----------------------------

def escanear(caminho):

    duplicados = {}
    arquivos_grandes = []

    for raiz, dirs, arquivos in os.walk(caminho):

        for arquivo in arquivos:

            caminho_completo = os.path.join(raiz, arquivo)

            try:
                tamanho = os.path.getsize(caminho_completo)
            except:
                continue

            # detectar arquivos grandes
            if tamanho > TAMANHO_GRANDE:
                arquivos_grandes.append((caminho_completo, tamanho))

            # detectar duplicados
            hash_arquivo = calcular_hash(caminho_completo)

            if hash_arquivo:
                duplicados.setdefault(hash_arquivo, []).append(caminho_completo)

    return duplicados, arquivos_grandes


# ----------------------------
# RELATÓRIO
# ----------------------------

def relatorio(duplicados, arquivos_grandes):

    print("\n📊 RELATÓRIO\n")

    print("🪨 Arquivos grandes:\n")
    for caminho, tamanho in arquivos_grandes:
        print(f"{tamanho_legivel(tamanho)}  {caminho}")

    print("\n🧬 Arquivos duplicados:\n")

    for hash_valor, arquivos in duplicados.items():
        if len(arquivos) > 1:
            print("Duplicado:")
            for a in arquivos:
                print("   ", a)
            print()


# ----------------------------
# EXECUÇÃO
# ----------------------------

if __name__ == "__main__":

    print("🌳 Estrutura de diretórios:\n")
    mostrar_arvore(CAMINHO_INICIAL)

    print("\n🔎 Escaneando arquivos...\n")

    duplicados, grandes = escanear(CAMINHO_INICIAL)

    relatorio(duplicados, grandes)

<h1 align="center">🌳 disk-forensics-scanner </h1>

<p align="center">
  Um scanner avançado de filesystem feito em Python <br/>
  Analise diretórios, detecte arquivos duplicados e descubra arquivos gigantes diretamente no terminal.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-concluído-green"/>
  <img src="https://img.shields.io/badge/license-MIT-blue"/>
  <img src="https://img.shields.io/badge/python-3.x-yellow"/>
  <img src="https://img.shields.io/badge/interface-CLI-purple"/>
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg"/>
</p>

---

## 🧠 Sobre o Projeto

Este projeto é um **scanner de arquivos e diretórios** desenvolvido em Python que permite explorar a estrutura de um sistema de arquivos diretamente pelo terminal.

A ferramenta percorre diretórios, identifica padrões e gera relatórios úteis para análise de armazenamento.

Principais funcionalidades:

- 🌳 Visualização da estrutura de diretórios em formato de árvore
- 🔎 Escaneamento completo de arquivos
- 🧬 Detecção de arquivos duplicados através de hash MD5
- 🪨 Identificação de arquivos muito grandes
- 📊 Geração de relatório final com informações relevantes
- 🔒 Tratamento de permissões e erros do sistema

Durante o escaneamento, o sistema pode identificar:

- 📁 Diretórios
- 📄 Arquivos comuns
- 🧬 Arquivos duplicados
- 🪨 Arquivos grandes
- 🔒 Diretórios sem permissão de acesso

Esse projeto é interessante para estudar:

- manipulação de arquivos e diretórios
- estrutura de filesystem
- geração de hash de arquivos
- análise de uso de armazenamento
- automação de tarefas de sistema
- desenvolvimento de ferramentas CLI

---

## 🚀 Tecnologias Utilizadas

Este projeto foi desenvolvido com as seguintes tecnologias:

- ✅ Python 3
- ✅ os
- ✅ hashlib
- ✅ operações de filesystem
- ✅ algoritmos de hashing
- ✅ terminal/CLI

---

## ⚙️ Funcionalidades

### 🌳 Visualização em árvore

Mostra a estrutura do filesystem:

```
/
├── 📁 home
│ └── 📁 usuario
│ ├── 📄 notas.txt
│ └── 📄 projeto.py
├── 📁 etc
└── 📄 kernel.img
```


---

### 🧬 Detecção de arquivos duplicados

Arquivos com **conteúdo idêntico** são identificados através de hash MD5.

Exemplo:

```
Duplicado:
/home/user/foto1.jpg
/backup/foto1.jpg
```

---

### 🪨 Detecção de arquivos grandes

Arquivos acima de um limite configurável são listados no relatório.

Exemplo:

```
1.24GB /home/user/video.mp4
```


---

## 📦 Como usar

Clone o repositório:

```bash
git clone https://github.com/SEU_USUARIO/disk-forensics-scanner.git
cd disk-forensics-scanner
```

Execute o scanner:
```
python scanner.py
```


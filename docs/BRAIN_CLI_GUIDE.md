# Brain System CLI - Guia Completo

## 📖 Índice

1. [Introdução](#introdução)
2. [Instalação e Setup](#instalação-e-setup)
3. [Visão Geral dos Comandos](#visão-geral-dos-comandos)
4. [Referência de Comandos](#referência-de-comandos)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Configuração Avançada](#configuração-avançada)
7. [Solução de Problemas](#solução-de-problemas)

## Introdução

O Brain System é uma plataforma inteligente para:

- 🧠 **Processamento de ideias** via LLM
- 🔍 **Busca semântica** com RAG (Retrieval Augmented Generation)
- 🎯 **Gerenciamento de skills** customizáveis
- 📊 **Avaliação e melhoria** automática de skills
- 🤖 **Operação autônoma** com multi-agent orchestration

## Instalação e Setup

### Pré-requisitos

```bash
# Python 3.12+
python3 --version

# Dependências do projeto
cd /home/jonas/HD/brain_system
pip install -e .
```

### Primeira Execução

```bash
# Ver ajuda
./brain help

# Listar todos os comandos
./brain help --list

# Ver exemplos práticos
./brain help --examples
```

## Visão Geral dos Comandos

### Por Categoria

#### 📝 Notas e Second Brain
- `brain add` - Adicionar e processar nova nota automaticamente
- `brain search` - Buscar notas semânticas e contexto
- `brain optimize` - Otimizar todo o vault de notas

#### 🔍 Busca e Índice
- `brain search` - Buscar no índice RAG
- `brain index` - Reconstruir índice vetorial (avançado)

#### ⚙️ Manutenção Interna
- `brain refine` - Refinar notas existentes (interno/avançado)
- `brain skills list` - Listar skills internas
- `brain skills new` - Criar nova skill (interno)
- `brain skills show` - Ver conteúdo de skill (interno)
- `brain skills run` - Executar uma skill (interno)

#### 📊 Avaliação
- `brain eval` - Avaliar skill com conjunto de testes
- `brain eval-run` - Avaliação com orquestração de agentes
- `brain improve` - Melhorar skill baseado em análise

#### 🤖 Automação
- `brain autonomous` - Operação autônoma
- `brain watch` - Auto-commit automático

#### 🛠️ Manutenção
- `brain restructure` - Reorganizar vault

#### ❓ Ajuda
- `brain help` - Sistema completo de ajuda

## Referência de Comandos

### brain add

**Propósito**: Ingerir uma nota no Second Brain e aplicar o pipeline interno de processamento

**Sintaxe**:
```bash
brain add <conteúdo> [--model MODELO]
```

**Argumentos**:
- `conteúdo` - Texto da ideia a processar (pode usar aspas para múltiplas palavras)
- `--model` - Modelo LLM (openai, claude, ollama:modelo)

**Exemplos**:
```bash
# Exemplo simples
brain add "Como implementar cache em Python"

# Com modelo específico
brain add "Estrutura de permissões Linux" --model claude

# Múltiplas palavras
brain add "Preciso aprender Docker para containerização"
```

**Output**: Texto processado e estruturado da ideia

---

### brain search

**Propósito**: Buscar por notas relevantes no Second Brain com contexto semântico

**Sintaxe**:
```bash
brain search <consulta>
```

### brain optimize

**Propósito**: Executar a otimização completa do vault de notas, incluindo refinamento, relinking e re-indexação

**Sintaxe**:
```bash
brain optimize [--no-relink] [--no-reindex] [--cleanup] [--cleanup-days DIAS]
```

**Exemplo**:
```bash
brain optimize
brain optimize --cleanup --cleanup-days 90
```

### brain skills

**Propósito**: Buscar por notas relevantes no Second Brain com contexto semântico

**Sintaxe**:
```bash
brain search <consulta>
```

**Argumentos**:
- `consulta` - Termo(s) de busca

**Exemplos**:
```bash
brain search "permissões de arquivo"
brain search "como configurar nginx"
brain search "python async"
```

**Output**: Lista ordenada de documentos relevantes

---

### brain skills

**Propósito**: Gerenciar skills locais internamente (uso avançado; normalmente não necessário para usuários do Second Brain)

#### brain skills list

Lista todas as skills disponíveis:
```bash
brain skills list
```

#### brain skills show

Exibe conteúdo de uma skill:
```bash
brain skills show brain_orchestrator
brain skills show note_refinement
```

#### brain skills new

Cria novo template de skill:
```bash
# Com objetivo
brain skills new classificador_markdown --goal "Classificar notas por categoria"

# Sem objetivo (será pedido depois)
brain skills new minha_skill
```

#### brain skills run

Executa uma skill:
```bash
# Execução básica
brain skills run brain_orchestrator --target vault/notes/

# Com instrução customizada
brain skills run brain_orchestrator --instruction "Organizar por categoria"

# Apenas visualizar prompt (sem executar)
brain skills run brain_orchestrator --target vault/notes/ --dry-run

# Com modelo específico
brain skills run minha_skill --target vault/notes/ --model claude
```

---

### brain eval

**Propósito**: Avaliar skill com conjunto de testes

**Sintaxe**:
```bash
brain eval --eval-set ARQUIVO --skill SKILL [opções]
```

**Argumentos principais**:
- `--eval-set` - Arquivo JSON com casos de teste
- `--skill` - Nome da skill a avaliar
- `--num-workers` - Workers paralelos (padrão: 10)
- `--timeout` - Timeout por query em segundos (padrão: 30)
- `--model` - Modelo LLM a usar

**Exemplos**:
```bash
# Avaliação básica
brain eval --eval-set tests/eval.json --skill brain_orchestrator

# Com múltiplos workers
brain eval --eval-set tests/eval.json --skill minha_skill --num-workers 5

# Com modelo customizado
brain eval --eval-set tests/eval.json --skill brain_orchestrator --model claude

# Modo verboso
brain eval --eval-set tests/eval.json --skill minha_skill --verbose
```

**Output**: Relatório com métricas de sucesso

---

### brain improve

**Propósito**: Melhorar skill baseado em análise de execução

**Sintaxe**:
```bash
brain improve --skill SKILL --analysis ARQUIVO [opções]
```

**Argumentos**:
- `--skill` - Nome da skill a melhorar
- `--analysis` - Arquivo de análise (JSON ou Markdown)
- `--version` - Versão da skill melhorada
- `--model` - Modelo LLM para melhoria

**Exemplos**:
```bash
# Melhoria básica
brain improve --skill minha_skill --analysis analysis.json

# Com versão específica
brain improve --skill brain_orchestrator --analysis results.md --version 2

# Com modelo customizado
brain improve --skill minha_skill --analysis analysis.json --model claude
```

**Output**: Caminho da skill melhorada

---

### brain autonomous

**Propósito**: Modo autônomo de operação

**Sintaxe**:
```bash
brain autonomous [--model MODELO] [--max-cycles N]
```

**Argumentos**:
- `--model` - Modelo LLM a usar
- `--max-cycles` - Número máximo de ciclos (padrão: 10)

**Exemplos**:
```bash
# Uso básico (10 ciclos padrão)
brain autonomous

# Ciclos customizados
brain autonomous --max-cycles 5

# Com modelo específico
brain autonomous --model claude --max-cycles 20
```

**Como funciona**:
1. Sistema seleciona uma tarefa baseado em objetivos
2. Executa pipeline multi-agente
3. Coleta métricas de performance
4. Aplica melhorias automáticas
5. Repete até atingir max-cycles

---

### brain help

**Propósito**: Sistema de ajuda interativo

**Sintaxe**:
```bash
brain help [COMANDO] [opções]
```

**Opções**:
- `--list` - Lista todos os comandos por categoria
- `--quick` - Referência rápida de comandos frequentes
- `--examples` - Guia com exemplos práticos

**Exemplos**:
```bash
# Ajuda geral
brain help

# Ajuda de comando específico
brain help add
brain help skills
brain help eval

# Lista completa
brain help --list

# Referência rápida
brain help --quick

# Exemplos práticos
brain help --examples
```

## Exemplos Práticos

### Workflow 1: Começar com Nova Nota

```bash
# 1. Adicionar a ideia
brain add "Aprendi sobre async/await em Python"

# 2. Atualizar índice
brain index

# 3. Verificar se foi indexada
brain search "async await python"
```

### Workflow 2: Criar e Testar Skill

```bash
# 1. Criar template
brain skills new extrator_codigo --goal "Extrair blocos de código"

# 2. Ver template (editar conforme necessário)
brain skills show extrator_codigo

# 3. Testar sem executar (ver prompt)
brain skills run extrator_codigo --target vault/notes/ --dry-run

# 4. Executar
brain skills run extrator_codigo --target vault/notes/
```

### Workflow 3: Avaliar e Melhorar Skill

```bash
# 1. Criar arquivo de avaliação (tests/eval_extrator.json)
cat > tests/eval_extrator.json << 'EOF'
[
  {
    "id": "test_1",
    "instruction": "Extrair código do arquivo",
    "target": "vault/notes/Python.md",
    "expectations": "Deve extrair blocos de código Python"
  }
]
EOF

# 2. Avaliar
brain eval --eval-set tests/eval_extrator.json --skill extrator_codigo

# 3. Analisar resultados e criar arquivo de análise
# (Salvar análise em analysis.json)

# 4. Melhorar
brain improve --skill extrator_codigo --analysis analysis.json --version 2

# 5. Verificar nova versão
brain skills show extrator_codigo
```

### Workflow 4: Operação Autônoma

```bash
# Iniciar modo autônomo com 5 ciclos
brain autonomous --max-cycles 5

# Ver logs de observabilidade
cat logs/observability.jsonl | tail -20

# Ver plano de melhorias
cat logs/improvements.log
```

## Configuração Avançada

### Variáveis de Ambiente

```bash
# Modelo LLM padrão
export BRAIN_MODEL=claude

# API Key OpenAI
export OPENAI_API_KEY=sk-...

# API Key Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Ativar debug
export BRAIN_DEBUG=1
```

### Estrutura de Diretórios

```
brain_system/
├── vault/
│   ├── notes/           # Notas principais
│   ├── archive/         # Notas arquivadas
│   ├── attachments/     # Arquivos anexados
│   ├── inbox/           # Entrada rápida
│   └── templates/       # Templates de notas
├── skills/              # Skills customizáveis
├── logs/
│   ├── observability.jsonl  # Métricas de execução
│   └── improvements.log     # Histórico de melhorias
├── tests/               # Testes e eval sets
└── runs/                # Resultados de execuções
```

### Criar Script Customizado

```bash
#!/bin/bash
# scripts/meu_workflow.sh

# Workflow automático personalizado
brain add "Minha ideia diária"
brain index
brain skills run meu_classificador --target vault/notes/
brain search "termo importante"
```

## Solução de Problemas

### Erro: "comando não encontrado"

```bash
# Certifique-se que o brain está no PATH
chmod +x ./brain
export PATH="$PATH:$(pwd)"

# Ou use diretamente
./brain help
```

### Erro: "Módulo não encontrado"

```bash
# Instalar dependências
pip install -e .

# Verificar instalação
python3 -c "import brain_system; print(brain_system.__file__)"
```

### Erro: "API Key não encontrada"

```bash
# Configurar variável de ambiente
export OPENAI_API_KEY=sua_chave

# Ou criar arquivo .env
echo "OPENAI_API_KEY=sua_chave" > .env
source .env
```

### Skill não aparece em `brain skills list`

```bash
# Verificar estrutura de diretórios
ls -la skills/

# Skill deve ter SKILL.md
ls -la skills/minha_skill/SKILL.md
```

### Índice RAG está lento

```bash
# Reconstruir índice
brain index

# Verificar tamanho
du -sh . # Tamanho total
wc -l vault/notes/*.md # Número de linhas
```

## Dicas e Truques

### 1. Usar Alias

```bash
# Adicionar ao ~/.bashrc ou ~/.zshrc
alias b='brain'
alias bs='brain skills'
alias bsr='brain search'

# Depois usar
b help
bs list
bsr "termo"
```

### 2. Monitorar Observabilidade

```bash
# Ver últimas execuções
tail -f logs/observability.jsonl

# Contar execuções bem-sucedidas
grep '"success": true' logs/observability.jsonl | wc -l
```

### 3. Batch Processing

```bash
# Processar múltiplas notas
for file in vault/notes/*.md; do
  brain refine "$file" --model claude
done
```

### 4. Modo Dry-Run

```bash
# Sempre use --dry-run para visualizar prompts
brain skills run skill_nova --target vault/notes/ --dry-run

# Redirecionar para arquivo
brain skills run skill_nova --target vault/notes/ --dry-run > prompt.txt
```

---

## Suporte e Contribuição

Para mais informações, acesse:
- GitHub: [brain-system](https://github.com/seu-user/brain-system)
- Documentação: [README.md](./README.md)
- Versão: v0.4.1 ou superior

**Última atualização**: Abril 2026

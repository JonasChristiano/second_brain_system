# Brain System - Instalação e Configuração

## 🔧 Instalação Local

### 1. Instalação Padrão

```bash
cd /home/jonas/HD/brain_system

# Instalar em modo editable
pip install -e .

# Verificar instalação
python3 -c "import brain_system; print(brain_system.__file__)"
```

### 2. Fazer Executável Global

```bash
# Tornar script executável
chmod +x ./brain

# Opção A: Adicionar ao PATH
export PATH="$PATH:/home/jonas/HD/brain_system"

# Opção B: Criar symlink em /usr/local/bin
sudo ln -s /home/jonas/HD/brain_system/brain /usr/local/bin/brain

# Opção C: Criar alias em ~/.bashrc
echo "alias brain='/home/jonas/HD/brain_system/brain'" >> ~/.bashrc
source ~/.bashrc
```

### 3. Verificar Instalação

```bash
# Testar comando
brain help

# Verificar versão
brain --version  # (se implementado)

# Ver localização
which brain
```

## 🌍 Variáveis de Ambiente

### Configuração Mínima

```bash
# Criar arquivo .env na raiz do projeto
cat > /home/jonas/HD/brain_system/.env << 'EOF'
# Modelo LLM padrão
BRAIN_MODEL=claude

# Chaves de API
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Diretórios customizados (opcional)
BRAIN_VAULT_DIR=/home/jonas/HD/brain_system/vault
BRAIN_SKILLS_DIR=/home/jonas/HD/brain_system/skills
BRAIN_LOGS_DIR=/home/jonas/HD/brain_system/logs
EOF

# Carregar no shell
source /home/jonas/HD/brain_system/.env
```

### No ~/.bashrc ou ~/.zshrc

```bash
# Adicionar ao final do arquivo
export BRAIN_MODEL=claude
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Alias úteis
alias b='brain'
alias bs='brain skills'
alias bsr='brain search'
alias bh='brain help'

# Função helper
brain-setup() {
    cd /home/jonas/HD/brain_system
    source .env
    brain help
}
```

## 📋 Estrutura de Diretórios

```
/home/jonas/HD/brain_system/
├── brain              # Script executável
├── src/
│   └── brain_system/
│       ├── __init__.py
│       ├── cli.py
│       ├── help.py        # ← Sistema de help
│       ├── skills.py
│       ├── rag.py
│       ├── paths.py
│       ├── llm_adapter.py
│       ├── agents/        # Agentes autônomos
│       ├── llm/           # Clientes LLM
│       └── infra/         # Observabilidade
│
├── vault/
│   ├── notes/             # Notas principais
│   ├── archive/           # Arquivos antigos
│   ├── attachments/       # Anexos
│   ├── inbox/             # Entrada rápida
│   └── templates/         # Templates
│
├── skills/                # Skills customizáveis
│   ├── brain_orchestrator/
│   ├── note_refinement/
│   └── ...
│
├── tests/                 # Testes unitários
├── logs/
│   ├── observability.jsonl
│   └── improvements.log
│
├── runs/                  # Resultados de execuções
├── pyproject.toml         # Configuração Python
├── README.md
├── BRAIN_CLI_GUIDE.md     # Guia completo
├── CHEAT_SHEET.md         # Referência rápida
└── HELPER_SUMMARY.md      # Este arquivo
```

## 🎯 Primeiros Passos

### 1. Setup Inicial

```bash
cd /home/jonas/HD/brain_system

# Instalar dependências
pip install -e .

# Verificar testes
python3 tests/check_coverage.py

# Ver ajuda
./brain help
```

### 2. Configurar LLM

```bash
# Escolher provider (OpenAI, Claude ou Local)

# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# Local (Ollama)
# Instalar Ollama: https://ollama.ai
# ollama pull llama2
# ollama pull neural-chat
```

### 3. Primeira Execução

```bash
# Ver ajuda
./brain help

# Adicionar primeira nota
./brain add "Aprendendo Brain System"

# Indexar
./brain index

# Buscar
./brain search "Brain System"
```

## 🔍 Verificação de Saúde

```bash
#!/bin/bash
# scripts/health_check.sh

echo "🔍 Verificação de Saúde do Brain System"
echo "========================================"

# 1. Python
echo -n "Python: "
python3 --version

# 2. Dependências
echo -n "brain_system: "
python3 -c "import brain_system; print('OK')" 2>/dev/null || echo "FALHA"

# 3. Executável
echo -n "Script brain: "
[ -x ./brain ] && echo "OK" || echo "FALHA"

# 4. Testes
echo -n "Testes: "
python3 tests/check_coverage.py > /dev/null 2>&1 && echo "OK" || echo "FALHA"

# 5. Help
echo -n "Sistema de help: "
./brain help > /dev/null 2>&1 && echo "OK" || echo "FALHA"

echo "========================================"
echo "✓ Verificação concluída"
```

## 🐛 Troubleshooting

### Erro: "comando não encontrado"

```bash
# Solução 1: Use caminho completo
/home/jonas/HD/brain_system/brain help

# Solução 2: Adicione ao PATH
export PATH="$PATH:/home/jonas/HD/brain_system"

# Solução 3: Crie symlink
sudo ln -s /home/jonas/HD/brain_system/brain /usr/local/bin/brain
```

### Erro: "ModuleNotFoundError: No module named 'brain_system'"

```bash
# Instalar em modo editable
pip install -e /home/jonas/HD/brain_system

# Ou adicionar ao PYTHONPATH
export PYTHONPATH="$PYTHONPATH:/home/jonas/HD/brain_system/src"
```

### Erro: "API Key não encontrada"

```bash
# Verificar variáveis
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Configurar
export OPENAI_API_KEY="sk-..."
# ou
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Help não funciona

```bash
# Verificar se help.py existe
ls -la src/brain_system/help.py

# Testar help diretamente
python3 -c "from brain_system.help import HelpSystem; HelpSystem.print_header('teste')"
```

## 📦 Distribuição

### Para Outros Usuários

```bash
# 1. Package com pip
python3 -m pip install --upgrade build
python3 -m build

# 2. Fazer upload (PyPI)
python3 -m twine upload dist/*

# 3. Instalar globalmente
pip install brain-system

# Depois usar
brain help
```

## 🚀 Uso Diário

```bash
# Setup no shell
source ~/.bashrc  # Carregar aliases

# Usar
brain help                      # Ver ajuda
b add "Minha ideia"            # Usando alias
bs list                        # Listar skills
brain help --quick             # Referência rápida
```

## 📊 Performance

Para operações em larga escala:

```bash
# Otimizar índice
brain index --rebuild

# Monitore performance
watch -n 1 'tail logs/observability.jsonl'

# Parallel processing
brain eval --eval-set tests/eval.json --skill minha_skill --num-workers 10
```

## 🔐 Segurança

```bash
# Nunca commitar chaves de API
echo ".env" >> .gitignore
echo "logs/" >> .gitignore
echo "runs/" >> .gitignore

# Usar secrets manager (opcional)
# export $(cat .env | xargs)  # Somente local

# Auditar permissões
ls -la logs/
chmod 600 .env  # Arquivo sensível
```

## 📞 Suporte

Para problemas ou dúvidas:

1. Consulte `brain help --examples`
2. Leia `BRAIN_CLI_GUIDE.md`
3. Verifique `logs/observability.jsonl`
4. Abra issue no repositório

---

**Data**: Abril 2026
**Versão**: v0.4.1+
**Maintainer**: Jonas

# Brain System - Cheat Sheet

## 🚀 Quick Start

```bash
./brain help              # Ver ajuda geral
./brain help add          # Ajuda de comando específico
./brain help --list       # Ver todos os comandos
./brain help --quick      # Referência rápida
./brain help --examples   # Exemplos práticos
```

## 📝 Comandos Mais Usados

| Comando | Uso Rápido |
|---------|-----------|
| **add** | `brain add "ideia"` - Processar nova ideia |
| **search** | `brain search "termo"` - Buscar no RAG |
| **index** | `brain index` - Reconstruir índice |
| **skills list** | `brain skills list` - Listar skills |
| **skills run** | `brain skills run nome --target vault/notes/` - Executar skill |
| **eval** | `brain eval --eval-set tests/eval.json --skill nome` - Avaliar |
| **improve** | `brain improve --skill nome --analysis analysis.json` - Melhorar |
| **autonomous** | `brain autonomous --max-cycles 5` - Modo autônomo |
| **refine** | `brain refine vault/notes/file.md` - Refinar nota |
| **watch** | `brain watch` - Auto-commit |

## 🎯 Workflows Rápidos

### Adicionar e Indexar
```bash
brain add "Nova ideia aqui"
brain index
```

### Criar Skill
```bash
brain skills new minha_skill --goal "Objetivo"
brain skills show minha_skill          # Ver template
# Editar SKILL.md
brain skills run minha_skill --target vault/notes/ --dry-run
```

### Avaliar Skill
```bash
brain eval --eval-set tests/eval.json --skill minha_skill
```

### Melhorar Skill
```bash
brain improve --skill minha_skill --analysis analysis.json
```

## 🔧 Opções Comuns

```bash
--model <modelo>      # Usar modelo específico (openai, claude)
--target <caminho>    # Especificar alvo
--dry-run            # Apenas mostrar sem executar
--verbose            # Saída detalhada
--help               # Ajuda do comando
```

## 📊 Monitorar Sistema

```bash
# Ver últimas execuções
tail logs/observability.jsonl

# Ver melhorias aplicadas
cat logs/improvements.log

# Ver resultados de execução
ls -la runs/
```

## 🌐 Variáveis de Ambiente

```bash
export BRAIN_MODEL=claude
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export BRAIN_DEBUG=1
```

## 📚 Estrutura de Diretórios

```
.
├── vault/notes/         → Notas principais
├── skills/              → Skills customizáveis
├── tests/               → Eval sets
├── logs/
│   ├── observability.jsonl
│   └── improvements.log
└── runs/                → Resultados
```

## 💡 Dicas

1. **Use `--dry-run`** para visualizar prompts antes de executar
2. **Use `brain search`** para encontrar notas relacionadas
3. **Use `brain help <cmd>`** para documentação completa
4. **Configure alias**: `alias b='brain'` em `~/.bashrc`
5. **Use `--model claude`** para melhores resultados

## 🔗 Links Rápidos

- Guia completo: `BRAIN_CLI_GUIDE.md`
- Repositório: `https://github.com/user/brain-system`
- Issues: `https://github.com/user/brain-system/issues`

---
**Versão**: v0.3.0 | **Data**: Abril 2026
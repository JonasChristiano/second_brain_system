# 📚 Brain System - Documentação

Bem-vindo à documentação completa do **Brain System**! 

## 🚀 Comece Aqui

Escolha seu ponto de partida:

### Para Novos Usuários
1. **[INSTALLATION.md](INSTALLATION.md)** - Como instalar e configurar
2. **[CHEAT_SHEET.md](CHEAT_SHEET.md)** - Referência rápida (5 min)
3. Use `./brain help --examples` - Exemplos práticos no terminal

### Para Usuários Regulares
- **[CHEAT_SHEET.md](CHEAT_SHEET.md)** - Tabela rápida de comandos
- Use `./brain help <comando>` - Ajuda de comando específico
- Use `./brain help --quick` - Workflows rápidos

### Para Referência Completa
- **[BRAIN_CLI_GUIDE.md](BRAIN_CLI_GUIDE.md)** - Guia completo de todos os comandos
- **[NAVIGATION.md](NAVIGATION.md)** - Mapa de navegação (encontrar informação)

### Para Entender o Sistema
- **[README_HELP.md](README_HELP.md)** - Sumário do sistema de help
- **[HELPER_SUMMARY.md](HELPER_SUMMARY.md)** - Estatísticas e funcionalidades
- **[HELP_SUMMARY.txt](HELP_SUMMARY.txt)** - Diagrama visual ASCII

---

## 📖 Índice de Documentos

| Arquivo | Tamanho | Propósito | Para Quem |
|---------|---------|----------|----------|
| **[INSTALLATION.md](INSTALLATION.md)** | 550 linhas | Setup, instalação, configuração | Iniciantes |
| **[BRAIN_CLI_GUIDE.md](BRAIN_CLI_GUIDE.md)** | 400+ linhas | Referência de todos os comandos | Todos |
| **[CHEAT_SHEET.md](CHEAT_SHEET.md)** | 150 linhas | Tabela rápida + dicas | Uso diário |
| **[NAVIGATION.md](NAVIGATION.md)** | 330 linhas | Mapa de navegação visual | Encontrar info |
| **[README_HELP.md](README_HELP.md)** | ~300 linhas | Índice central do help | Referência |
| **[HELPER_SUMMARY.md](HELPER_SUMMARY.md)** | 200 linhas | Sumário executivo | Overview |
| **[HELP_SUMMARY.txt](HELP_SUMMARY.txt)** | 155 linhas | Diagrama ASCII visual | Visão geral |

---

## ⚡ Quick Links

### Instalação & Setup
- [Como Instalar](INSTALLATION.md#instalação-padrão)
- [Primeiros Passos](INSTALLATION.md#primeiros-passos)
- [Configurar Variáveis](INSTALLATION.md#variáveis-de-ambiente)
- [Troubleshooting](INSTALLATION.md#troubleshooting)

### Usar o Brain
- [Referência Rápida](CHEAT_SHEET.md)
- [Comandos por Categoria](BRAIN_CLI_GUIDE.md#visão-geral-dos-comandos)
- [Exemplos Práticos](BRAIN_CLI_GUIDE.md#exemplos-práticos)
- [Workflows](CHEAT_SHEET.md#workflows-rápidos)

### Encontrar Informação
- [Mapa de Navegação](NAVIGATION.md)
- [Matriz de Comandos](NAVIGATION.md#-matriz-de-comandos)
- [Tabela de Tópicos](NAVIGATION.md#-donde-procurar-por-tópico)

---

## 🎯 Aprenda em 3 Etapas

### Etapa 1: Instalar (5 min)
```bash
cat docs/INSTALLATION.md | head -50
```

### Etapa 2: Aprender Rápido (5 min)
```bash
./brain help --quick
# ou
cat docs/CHEAT_SHEET.md
```

### Etapa 3: Praticar (10 min)
```bash
./brain help --examples
./brain add "Minha primeira ideia"
./brain search "teste"
```

---

## 💡 Sistema de Help Interativo

Além da documentação escrita, use o help integrado:

```bash
# Ajuda geral
./brain help

# Ajuda de comando específico
./brain help add
./brain help skills

# Lista de todos os comandos
./brain help --list

# Referência rápida
./brain help --quick

# Exemplos práticos
./brain help --examples
```

---

## 📊 Documentação em Números

```
✓ Linhas de Documentação:  2500+
✓ Arquivos:                7
✓ Comandos Documentados:   15+
✓ Exemplos de Uso:         40+
✓ Workflows Práticos:      7
✓ Testes:                  44/44 ✓
```

---

## 🔍 Encontrar Rapidamente

### "Quero instalar/configurar"
→ [INSTALLATION.md](INSTALLATION.md)

### "Quero ver a sintaxe de um comando"
→ Use `./brain help <comando>` ou [BRAIN_CLI_GUIDE.md](BRAIN_CLI_GUIDE.md)

### "Quero aprender rápido"
→ [CHEAT_SHEET.md](CHEAT_SHEET.md) ou `./brain help --quick`

### "Quero exemplos práticos"
→ `./brain help --examples` ou [BRAIN_CLI_GUIDE.md](BRAIN_CLI_GUIDE.md#exemplos-práticos)

### "Tenho um problema"
→ [INSTALLATION.md#troubleshooting](INSTALLATION.md#troubleshooting)

### "Não sei por onde começar"
→ [NAVIGATION.md](NAVIGATION.md)

### "Quero entender tudo"
→ [BRAIN_CLI_GUIDE.md](BRAIN_CLI_GUIDE.md)

---

## 🎓 Plano de Aprendizado

### Dia 1: Fundamentos
- Ler: [INSTALLATION.md](INSTALLATION.md) (Setup)
- Fazer: `./brain help`
- Fazer: `./brain help --quick`

### Dia 2: Prática
- Ler: [CHEAT_SHEET.md](CHEAT_SHEET.md)
- Fazer: `./brain help --examples`
- Praticar: `./brain add "Teste"`

### Dia 3: Aprofundamento
- Ler: [BRAIN_CLI_GUIDE.md](BRAIN_CLI_GUIDE.md)
- Explorar: Todos os comandos
- Praticar: Workflows

### Semana 2+: Avançado
- Ler: [BRAIN_CLI_GUIDE.md](BRAIN_CLI_GUIDE.md#configuração-avançada)
- Explorar: Automação e scripts
- Personalizar: Skills e workflows

---

## 📞 Precisa de Ajuda?

1. **Pergunta rápida** → Use `./brain help`
2. **Comando específico** → `./brain help <comando>`
3. **Referência completa** → [BRAIN_CLI_GUIDE.md](BRAIN_CLI_GUIDE.md)
4. **Problema de setup** → [INSTALLATION.md](INSTALLATION.md)
5. **Não sabe por onde começar** → [NAVIGATION.md](NAVIGATION.md)

---

## 📚 Estrutura de Pasta

```
docs/
├── README.md                    ← Você está aqui!
├── INSTALLATION.md              Setup & configuração
├── BRAIN_CLI_GUIDE.md           Referência completa
├── CHEAT_SHEET.md               Rápido & dicas
├── NAVIGATION.md                Mapa de navegação
├── README_HELP.md               Índice central
├── HELPER_SUMMARY.md            Sumário executivo
└── HELP_SUMMARY.txt             Diagrama visual
```

---

## ✨ Recursos

- **Help Interativo**: `./brain help` 
- **Código**: `src/brain_system/help.py`
- **Testes**: `tests/check_coverage.py`
- **Repositório**: GitHub (veja README principal)

---

## 🎉 Próximas Leituras

1. [INSTALLATION.md](INSTALLATION.md) - Se é novo
2. [CHEAT_SHEET.md](CHEAT_SHEET.md) - Se quer referência rápida
3. [BRAIN_CLI_GUIDE.md](BRAIN_CLI_GUIDE.md) - Se quer referência completa
4. [NAVIGATION.md](NAVIGATION.md) - Se quer encontrar algo

---

**Versão**: v0.3.0+  
**Data**: Abril 2026  
**Status**: ✅ Completo
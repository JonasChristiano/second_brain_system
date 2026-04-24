# Brain System - Mapa de Navegação e Índice

## 🗺️ Guia de Navegação da Documentação

### Para Usuários Iniciantes
```
1. Comece aqui → INSTALLATION.md (seção "Primeiros Passos")
2. Depois → brain help (no terminal)
3. Leia → CHEAT_SHEET.md (referência rápida)
4. Explore → brain help --examples (7 exemplos práticos)
```

### Para Usuários Intermediários
```
1. Referência → BRAIN_CLI_GUIDE.md (guia completo)
2. Quick look → brain help --quick (workflows frequentes)
3. Comando específico → brain help <comando>
4. Troubleshooting → INSTALLATION.md (seção de troubleshooting)
```

### Para Usuários Avançados
```
1. Código → src/brain_system/help.py (sistema de help)
2. CLI → src/brain_system/cli.py (integração)
3. Config → INSTALLATION.md (configuração avançada)
4. Automação → BRAIN_CLI_GUIDE.md (batch processing)
```

---

## 📁 Arquivos de Documentação

```
📚 DOCUMENTAÇÃO CRIADA

├── 🎯 INSTALLATION.md (554 linhas)
│   ├── Instalação local e global
│   ├── Configuração de variáveis
│   ├── Primeiros passos
│   ├── Verificação de saúde
│   ├── Troubleshooting
│   ├── Segurança
│   └── Distribuição
│
├── 📖 BRAIN_CLI_GUIDE.md (~400 linhas)
│   ├── Introdução e visão geral
│   ├── Referência completa de comandos
│   ├── 4 workflows práticos
│   ├── Configuração avançada
│   ├── Troubleshooting
│   ├── Dicas e truques
│   └── Aliases e scripts
│
├── ⚡ CHEAT_SHEET.md (~150 linhas)
│   ├── Quick start
│   ├── Tabela de comandos
│   ├── Workflows rápidos
│   ├── Opções comuns
│   ├── Monitoramento
│   └── Variáveis de ambiente
│
├── 📋 HELPER_SUMMARY.md (~200 linhas)
│   ├── O que foi criado
│   ├── Funcionalidades implementadas
│   ├── Cobertura de documentação
│   ├── Estatísticas
│   └── Arquivos modificados
│
└── 💻 src/brain_system/help.py (~700 linhas)
    ├── Classe HelpSystem
    ├── Documentação de 15+ comandos
    ├── Métodos de formatação
    ├── Sistema de categorias
    └── Integração com CLI
```

---

## 🎯 Encontrar Informação Rapidamente

### "Como uso o Brain?"
```
→ brain help
→ INSTALLATION.md: "Primeiros Passos"
→ CHEAT_SHEET.md
```

### "Como faço [tarefa específica]?"
```
→ brain help --examples (7 exemplos práticos)
→ BRAIN_CLI_GUIDE.md: "Exemplos Práticos"
```

### "Qual é o comando para [ação]?"
```
→ brain help --quick (workflows rápidos)
→ brain help --list (lista por categoria)
→ CHEAT_SHEET.md: "Comandos Mais Usados"
```

### "Qual é a sintaxe de [comando]?"
```
→ brain help <comando> (ajuda detalhada)
→ BRAIN_CLI_GUIDE.md: "Referência de Comandos"
```

### "Como configuro [opção]?"
```
→ INSTALLATION.md: "Variáveis de Ambiente"
→ BRAIN_CLI_GUIDE.md: "Configuração Avançada"
```

### "Como resolvo [problema]?"
```
→ INSTALLATION.md: "Troubleshooting"
→ BRAIN_CLI_GUIDE.md: "Solução de Problemas"
```

### "Preciso de exemplos práticos"
```
→ brain help --examples
→ BRAIN_CLI_GUIDE.md: "Exemplos Práticos"
→ CHEAT_SHEET.md: "Workflows Rápidos"
```

### "Como automatizo tarefas?"
```
→ BRAIN_CLI_GUIDE.md: "Configuração Avançada"
→ brain help autonomous
→ INSTALLATION.md: "scripts/health_check.sh"
```

---

## 🔗 Árvore de Ajuda Interativa

```
brain help
├── (sem opções) → Bem-vindo + comandos principais + dicas
│
├── help <comando>
│   ├── help add → Detalhes do comando add
│   ├── help skills → Detalhes + subcomandos
│   ├── help eval → Detalhes com argumentos
│   └── help autonomous → Detalhes de modo autônomo
│
├── help --list → Lista todos os comandos por categoria
│   ├── Processamento de Ideias
│   ├── Busca e Recuperação
│   ├── Gerenciamento de Skills
│   ├── Avaliação de Skills
│   ├── ... (9 categorias total)
│   └── Ajuda
│
├── help --quick → Workflows pré-definidos rápidos
│   ├── Processar nova ideia (2 comandos)
│   ├── Buscar informação (1 comando)
│   ├── Criar e testar skill (3 comandos)
│   ├── Avaliar skill (2 comandos)
│   └── Modo autônomo (1 comando)
│
└── help --examples → 7 exemplos práticos passo-a-passo
    ├── 1. Começar com nova nota
    ├── 2. Buscar conteúdo no vault
    ├── 3. Criar nova skill
    ├── 4. Testar skill
    ├── 5. Avaliar performance
    ├── 6. Melhorar skill
    └── 7. Modo autônomo
```

---

## 📊 Matriz de Comandos

| Comando | Ajuda Rápida | Guia Completo | Exemplo | Workflow |
|---------|-------------|---------------|---------|----------|
| **add** | ✓ | ✓ | ✓ | ✓ |
| **search** | ✓ | ✓ | ✓ | ✓ |
| **index** | ✓ | ✓ | - | ✓ |
| **skills** | ✓ | ✓ | ✓ | ✓ |
| **eval** | ✓ | ✓ | ✓ | ✓ |
| **improve** | ✓ | ✓ | ✓ | ✓ |
| **autonomous** | ✓ | ✓ | ✓ | ✓ |
| **refine** | ✓ | ✓ | - | ✓ |
| **watch** | ✓ | ✓ | - | - |
| **restructure** | ✓ | ✓ | - | - |

---

## 💡 Dicas de Navegação

### 1. Use o Terminal para Ajuda Rápida
```bash
# Ajuda geral
brain help

# Comando específico
brain help add

# Referência rápida
brain help --quick

# Exemplos
brain help --examples
```

### 2. Use Markdown para Leitura Offline
```bash
# Guia completo (pode salvar/imprimir)
cat BRAIN_CLI_GUIDE.md

# Cheat sheet (imprimir como poster)
cat CHEAT_SHEET.md

# Instalação (ler antes de começar)
cat INSTALLATION.md
```

### 3. Use Busca em Arquivos
```bash
# Buscar comando em guia
grep -n "brain add" BRAIN_CLI_GUIDE.md

# Buscar argumento
grep -n "\-\-model" BRAIN_CLI_GUIDE.md

# Buscar exemplo
grep -n "example" CHEAT_SHEET.md
```

### 4. Use Aliases para Acesso Rápido
```bash
# Adicionar ao ~/.bashrc
alias bh='brain help'
alias bhl='brain help --list'
alias bhq='brain help --quick'
alias bhe='brain help --examples'

# Depois
bh                  # Ajuda geral
bh add              # Ajuda de comando
bhl                 # Lista todos
bhq                 # Referência rápida
bhe                 # Exemplos
```

---

## 🎓 Plano de Aprendizado

### Semana 1: Fundamentos
```
Dia 1: brain help → Entender comandos principais
Dia 2: INSTALLATION.md → Setup completo
Dia 3: brain help --quick → Workflows frequentes
Dia 4: brain help --examples → Praticar 3 exemplos
Dia 5: CHEAT_SHEET.md → Memorizar comandos principais
Dia 6: Praticar: add, search, index
Dia 7: Praticar: skills list, show, run
```

### Semana 2: Skills
```
Dia 1: brain help skills → Entender subcomandos
Dia 2: Praticar: skills new, show
Dia 3: Praticar: skills run --dry-run
Dia 4: Ler: BRAIN_CLI_GUIDE.md (Workflow 3)
Dia 5: Praticar: criar nova skill
Dia 6: Ler: BRAIN_CLI_GUIDE.md (Workflow 4)
Dia 7: Praticar: eval e improve
```

### Semana 3: Avançado
```
Dia 1: brain help autonomous → Entender modo autônomo
Dia 2: BRAIN_CLI_GUIDE.md (Configuração Avançada)
Dia 3: INSTALLATION.md (Config de ambiente)
Dia 4: Praticar: batch processing
Dia 5: Praticar: aliases e scripts
Dia 6: Troubleshooting (INSTALLATION.md)
Dia 7: Projeto pessoal
```

---

## 📞 Donde Procurar por Tópico

| Tópico | Arquivo | Seção |
|--------|---------|-------|
| **Setup inicial** | INSTALLATION.md | "Instalação Padrão" |
| **Primeiros passos** | INSTALLATION.md | "Primeiros Passos" |
| **Referência de comandos** | BRAIN_CLI_GUIDE.md | "Referência de Comandos" |
| **Variáveis de ambiente** | INSTALLATION.md | "Variáveis de Ambiente" |
| **Troubleshooting** | INSTALLATION.md | "Troubleshooting" |
| **Exemplos práticos** | brain help --examples | Terminal |
| **Workflows rápidos** | brain help --quick | Terminal |
| **Lista de comandos** | brain help --list | Terminal |
| **Segurança** | INSTALLATION.md | "Segurança" |
| **Automatização** | BRAIN_CLI_GUIDE.md | "Configuração Avançada" |
| **Aliases** | BRAIN_CLI_GUIDE.md | "Dicas e Truques" |

---

## ✅ Checklist de Verificação

Ao usar o Brain System, consulte:

- [ ] Conhece o comando certo? → `brain help --quick`
- [ ] Quer sintaxe completa? → `brain help <comando>`
- [ ] Quer exemplos? → `brain help --examples`
- [ ] Quer lista? → `brain help --list`
- [ ] Tem problema? → `INSTALLATION.md` (Troubleshooting)
- [ ] Quer configurar? → `INSTALLATION.md` (Variáveis)
- [ ] Quer otimizar? → `BRAIN_CLI_GUIDE.md` (Config Avançada)
- [ ] Quer automatizar? → `BRAIN_CLI_GUIDE.md` (Batch Processing)

---

## 🎯 Próximas Leituras Sugeridas

1. **Começando**: INSTALLATION.md
2. **Fundamentos**: brain help
3. **Prática**: brain help --examples
4. **Referência**: CHEAT_SHEET.md
5. **Completo**: BRAIN_CLI_GUIDE.md
6. **Avançado**: BRAIN_CLI_GUIDE.md (Configuração Avançada)

---

**Última atualização**: Abril 2026
**Documentação total**: 2500+ linhas
**Comandos documentados**: 15+
**Exemplos inclusos**: 40+
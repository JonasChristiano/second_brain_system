"""
Sistema de ajuda completo para o Brain CLI.

Fornece documentação detalhada, exemplos de uso e guia interativo.
"""

from __future__ import annotations

from typing import Any


class HelpSystem:
    """Sistema centralizado de ajuda para o Brain CLI."""

    COMMANDS = {
        "add": {
            "name": "add",
            "category": "Processamento de Ideias",
            "description": "Processa uma ideia ou conteúdo via brain_orchestrator.",
            "syntax": "brain add <conteúdo> [--model MODELO]",
            "examples": [
                "brain add 'Como implementar um sistema de cache'",
                "brain add 'Estrutura de diretórios Linux' --model claude",
            ],
            "arguments": [
                {
                    "name": "conteúdo",
                    "required": True,
                    "description": "Texto da ideia a ser processada",
                },
                {
                    "name": "--model",
                    "required": False,
                    "description": "Modelo LLM a usar (openai, claude, gemini, ollama:modelo)",
                },
            ],
            "details": "Utiliza a skill brain_orchestrator para estruturar e processar ideias, salvando-as no vault.",
            "output": "Texto processado e estruturado da ideia",
        },
        "search": {
            "name": "search",
            "category": "Busca e Recuperação",
            "description": "Busca conteúdo no índice vetorial RAG.",
            "syntax": "brain search <consulta>",
            "examples": [
                "brain search 'permissões de arquivo'",
                "brain search 'como configurar docker'",
            ],
            "arguments": [
                {
                    "name": "consulta",
                    "required": True,
                    "description": "Termo de busca no índice vetorial",
                },
            ],
            "details": "Realiza busca semântica no índice vetorial. Retorna documentos relevantes ordenados por similaridade.",
            "output": "Lista de documentos e trechos relevantes com scores de relevância",
        },
        "index": {
            "name": "index",
            "category": "Índice RAG",
            "description": "Reconstrói o índice vetorial completo.",
            "syntax": "brain index",
            "examples": [
                "brain index",
            ],
            "arguments": [],
            "details": "Processa todas as notas no vault/notes e reconstrói o índice vetorial ChromaDB. Execute após adicionar muitas notas.",
            "output": "Status da construção do índice",
        },
        "watch": {
            "name": "watch",
            "category": "Automação",
            "description": "Ativa auto-commit automático para mudanças no vault.",
            "syntax": "brain watch",
            "examples": [
                "brain watch",
            ],
            "arguments": [],
            "details": "Monitora mudanças no vault e faz commits automáticos. Útil para tracking de histórico.",
            "output": "Logs de commits automáticos",
        },
        "restructure": {
            "name": "restructure",
            "category": "Manutenção",
            "description": "Reorganiza vault existente para estrutura padrão do projeto.",
            "syntax": "brain restructure",
            "examples": [
                "brain restructure",
            ],
            "arguments": [],
            "details": "Reestrutura o vault para seguir a organização padrão (archive, attachments, inbox, notes, templates).",
            "output": "Relatório de arquivos movidos/reorganizados",
        },
        "refine": {
            "name": "refine",
            "category": "Refinamento",
            "description": "Aplica skill de refinamento em notas.",
            "syntax": "brain refine [ARQUIVO] [--instruction INSTRUÇÃO] [--model MODELO]",
            "examples": [
                "brain refine vault/notes/Estrutura.md",
                "brain refine --instruction 'Melhorar formatação'",
                "brain refine vault/notes/ --model claude",
            ],
            "arguments": [
                {
                    "name": "ARQUIVO",
                    "required": False,
                    "description": "Arquivo específico a refinar (padrão: vault/notes/)",
                },
                {
                    "name": "--instruction",
                    "required": False,
                    "description": "Instrução personalizada para refinamento",
                },
                {
                    "name": "--model",
                    "required": False,
                    "description": "Modelo LLM a usar (openai, claude, gemini, ollama:modelo)",
                },
            ],
            "details": "Aplica técnicas de refinamento e melhoria em notas existentes.",
            "output": "Notas refinadas e melhoradas",
        },
        "skills": {
            "name": "skills",
            "category": "Gerenciamento de Skills",
            "description": "Gerencia skills locais (listar, criar, executar, mostrar).",
            "syntax": "brain skills <subcomando> [opções]",
            "examples": [
                "brain skills list",
                "brain skills show brain_orchestrator",
                "brain skills new minha_skill --goal 'Fazer algo útil'",
                "brain skills run minha_skill --target vault/notes/",
            ],
            "subcommands": {
                "list": {
                    "description": "Lista todas as skills disponíveis",
                    "syntax": "brain skills list",
                    "example": "brain skills list",
                },
                "show": {
                    "description": "Exibe conteúdo de uma skill",
                    "syntax": "brain skills show <nome>",
                    "example": "brain skills show note_refinement",
                    "arguments": ["nome: Nome da skill a exibir"],
                },
                "new": {
                    "description": "Cria um template de nova skill",
                    "syntax": "brain skills new <nome> [--goal OBJETIVO]",
                    "example": "brain skills new classificador --goal 'Classificar notas por categoria'",
                    "arguments": [
                        "nome: Nome da nova skill",
                        "--goal: Objetivo principal (opcional)",
                    ],
                },
                "run": {
                    "description": "Executa uma skill com o LLM",
                    "syntax": "brain skills run <nome> [--target ALVO] [--instruction INSTRUÇÃO] [--model MODELO] [--dry-run]",
                    "example": "brain skills run brain_orchestrator --target vault/notes/ --instruction 'Organizar por categoria'",
                    "arguments": [
                        "nome: Nome da skill a executar",
                        "--target: Caminho/escopo de execução",
                        "--instruction: Instrução complementar",
                        "--model: Modelo LLM a usar (openai, claude, gemini, ollama:modelo)",
                        "--dry-run: Mostrar prompt sem executar",
                    ],
                },
            },
        },
        "eval": {
            "name": "eval",
            "category": "Avaliação de Skills",
            "description": "Avalia skill usando conjunto de testes.",
            "syntax": "brain eval --eval-set ARQUIVO --skill SKILL [opções]",
            "examples": [
                "brain eval --eval-set tests/eval.json --skill brain_orchestrator",
                "brain eval --eval-set tests/eval.json --skill minha_skill --num-workers 5",
            ],
            "arguments": [
                {
                    "name": "--eval-set",
                    "required": True,
                    "description": "Caminho para arquivo JSON com casos de teste",
                },
                {
                    "name": "--skill",
                    "required": True,
                    "description": "Nome da skill a avaliar",
                },
                {
                    "name": "--num-workers",
                    "required": False,
                    "description": "Número de workers paralelos (padrão: 10)",
                },
                {
                    "name": "--timeout",
                    "required": False,
                    "description": "Timeout por query em segundos (padrão: 30)",
                },
                {
                    "name": "--runs-per-query",
                    "required": False,
                    "description": "Número de execuções por query (padrão: 3)",
                },
                {
                    "name": "--trigger-threshold",
                    "required": False,
                    "description": "Limite de trigger rate (padrão: 0.5)",
                },
                {
                    "name": "--model",
                    "required": False,
                    "description": "Modelo LLM a usar (openai, claude, gemini, ollama:modelo)",
                },
                {
                    "name": "--verbose",
                    "required": False,
                    "description": "Saída detalhada",
                },
            ],
            "details": "Executa conjunto completo de testes (eval set) contra uma skill para medir performance.",
            "output": "Relatório de avaliação com métrica de sucesso",
        },
        "eval-run": {
            "name": "eval-run",
            "category": "Avaliação de Skills",
            "description": "Executa pipeline de avaliação com orquestração de agentes.",
            "syntax": "brain eval-run --eval-set ARQUIVO --skill SKILL [--model MODELO]",
            "examples": [
                "brain eval-run --eval-set tests/eval.json --skill brain_orchestrator",
            ],
            "arguments": [
                {
                    "name": "--eval-set",
                    "required": True,
                    "description": "Caminho para arquivo JSON com casos de teste",
                },
                {
                    "name": "--skill",
                    "required": True,
                    "description": "Nome da skill a avaliar",
                },
                {
                    "name": "--model",
                    "required": False,
                    "description": "Modelo LLM a usar",
                },
            ],
            "details": "Similar a 'eval' mas usa o pipeline de agentes autônomos para orquestração.",
            "output": "Relatório detalhado com múltiplas métricas",
        },
        "improve": {
            "name": "improve",
            "category": "Melhoria de Skills",
            "description": "Melhora uma skill baseado em análise de execução.",
            "syntax": "brain improve --skill SKILL --analysis ARQUIVO [--model MODELO] [--version VERSÃO]",
            "examples": [
                "brain improve --skill minha_skill --analysis analysis.json",
                "brain improve --skill brain_orchestrator --analysis results.md --version 2",
            ],
            "arguments": [
                {
                    "name": "--skill",
                    "required": True,
                    "description": "Nome da skill a aprimorar",
                },
                {
                    "name": "--analysis",
                    "required": True,
                    "description": "Arquivo JSON/MD com análise de execução",
                },
                {
                    "name": "--model",
                    "required": False,
                    "description": "Modelo LLM a usar para melhoria",
                },
                {
                    "name": "--version",
                    "required": False,
                    "description": "Número da versão melhorada (salva em skills/<skill>/v<version>/)",
                },
            ],
            "details": "Analisa resultados de execução e gera versão melhorada da skill automaticamente.",
            "output": "Caminho da skill melhorada",
        },
        "autonomous": {
            "name": "autonomous",
            "category": "Modo Autônomo",
            "description": "Inicia operação autônoma do sistema.",
            "syntax": "brain autonomous [--model MODELO] [--max-cycles N]",
            "examples": [
                "brain autonomous",
                "brain autonomous --max-cycles 5",
                "brain autonomous --model claude --max-cycles 10",
            ],
            "arguments": [
                {
                    "name": "--model",
                    "required": False,
                    "description": "Modelo LLM a usar (padrão: configurado)",
                },
                {
                    "name": "--max-cycles",
                    "required": False,
                    "description": "Número máximo de ciclos autônomos (padrão: 10)",
                },
            ],
            "details": "Inicia modo autônomo onde o sistema seleciona tarefas, executa pipelines multi-agente e melhora-se automaticamente.",
            "output": "Logs de ciclos autônomos com resultados e melhorias",
        },
        "optimize": {
            "name": "optimize",
            "category": "Otimização",
            "description": "Otimiza o vault através de refinamento, relinking e re-indexação.",
            "syntax": "brain optimize [--no-relink] [--no-reindex] [--cleanup] [--cleanup-days DIAS]",
            "examples": [
                "brain optimize",
                "brain optimize --no-relink",
                "brain optimize --cleanup --cleanup-days 60",
            ],
            "arguments": [
                {
                    "name": "--no-relink",
                    "required": False,
                    "description": "Desabilita re-linking automático.",
                },
                {
                    "name": "--no-reindex",
                    "required": False,
                    "description": "Desabilita re-indexação.",
                },
                {
                    "name": "--cleanup",
                    "required": False,
                    "description": "Arquiva notas antigas durante a otimização.",
                },
                {
                    "name": "--cleanup-days",
                    "required": False,
                    "description": "Dias de inatividade antes de arquivar (padrão: 90).",
                },
            ],
            "details": "Executa uma otimização completa do vault, refinando notas, atualizando links e reindexando o conteúdo.",
            "output": "Resumo das ações realizadas e status de otimização",
        },
        "help": {
            "name": "help",
            "category": "Ajuda",
            "description": "Exibe ajuda detalhada sobre comandos.",
            "syntax": "brain help [COMANDO]",
            "examples": [
                "brain help",
                "brain help add",
                "brain help skills",
            ],
            "arguments": [
                {
                    "name": "COMANDO",
                    "required": False,
                    "description": "Comando específico para ajuda (opcional)",
                },
            ],
            "details": "Sistema de ajuda interativo com exemplos e documentação completa.",
            "output": "Documentação do comando",
        },
    }

    @staticmethod
    def print_header(title: str, width: int = 80) -> None:
        """Imprime um header formatado."""
        print("\n" + "=" * width)
        print(f" {title}".ljust(width - 1))
        print("=" * width + "\n")

    @staticmethod
    def print_section(title: str, width: int = 80) -> None:
        """Imprime um subtítulo de seção."""
        print(f"\n{title}")
        print("-" * len(title))

    @staticmethod
    def print_command_list() -> None:
        """Exibe lista de todos os comandos organizados por categoria."""
        HelpSystem.print_header("BRAIN SYSTEM - REFERÊNCIA DE COMANDOS")

        # Agrupar por categoria
        categories: dict[str, list[str]] = {}
        for cmd_name, cmd_info in HelpSystem.COMMANDS.items():
            cat = cmd_info.get("category", "Outros")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(cmd_name)

        # Exibir por categoria
        for category in sorted(categories.keys()):
            HelpSystem.print_section(category)
            for cmd_name in sorted(categories[category]):
                cmd = HelpSystem.COMMANDS[cmd_name]
                desc = cmd.get("description", "Sem descrição")
                print(f"  {cmd_name:15} - {desc}")
                if cmd.get("subcommands"):
                    for subcmd_name, subcmd_info in cmd["subcommands"].items():
                        sub_desc = subcmd_info.get("description", "Sem descrição")
                        print(f"    {subcmd_name:13} - {sub_desc}")

        HelpSystem._print_usage_tips()

    @staticmethod
    def print_command_help(cmd_name: str) -> None:
        """Exibe ajuda detalhada para um comando específico."""
        if cmd_name not in HelpSystem.COMMANDS:
            print(f"Comando '{cmd_name}' não encontrado.\n")
            print("Use 'brain help' para ver todos os comandos disponíveis.")
            return

        cmd = HelpSystem.COMMANDS[cmd_name]

        HelpSystem.print_header(f"COMANDO: {cmd_name.upper()}")

        # Descrição e categoria
        print(f"Categoria: {cmd.get('category', 'N/A')}")
        print(f"Descrição: {cmd.get('description', 'N/A')}\n")

        # Sintaxe
        HelpSystem.print_section("SINTAXE")
        print(f"  {cmd.get('syntax', 'N/A')}\n")

        # Detalhes
        if cmd.get("details"):
            HelpSystem.print_section("DETALHES")
            print(f"  {cmd.get('details')}\n")

        # Argumentos
        if cmd.get("arguments"):
            HelpSystem.print_section("ARGUMENTOS")
            for arg in cmd["arguments"]:
                required = "✓ obrigatório" if arg.get("required") else "  opcional"
                print(f"  {arg['name']:20} [{required}]")
                print(f"    {arg['description']}")
            print()

        # Subcomandos
        if cmd.get("subcommands"):
            HelpSystem.print_section("SUBCOMANDOS")
            for subcmd_name, subcmd_info in cmd["subcommands"].items():
                print(f"  {subcmd_name}")
                print(f"    {subcmd_info['description']}")
                print(f"    Uso: {subcmd_info['syntax']}")
                print(f"    Exemplo: {subcmd_info['example']}")
                print()

        # Exemplos
        if cmd.get("examples"):
            HelpSystem.print_section("EXEMPLOS")
            for example in cmd["examples"]:
                print(f"  $ {example}")
            print()

        # Output
        if cmd.get("output"):
            HelpSystem.print_section("SAÍDA")
            print(f"  {cmd.get('output')}\n")

        HelpSystem._print_usage_tips()

    @staticmethod
    def _print_usage_tips() -> None:
        """Exibe dicas de uso úteis."""
        print("\n" + "=" * 80)
        print("💡 DICAS")
        print("=" * 80)
        print("""
  • Use 'brain <comando> --help' para ajuda rápida de um comando
  • Use 'brain help <comando>' para documentação completa
  • A maioria dos comandos suporta --model para escolher o LLM
  • Use --dry-run em skills run para ver o prompt sem executar
  • Para mais informações, veja: docs/README.md ou docs/CHEAT_SHEET.md
""")

    @staticmethod
    def print_quick_reference() -> None:
        """Exibe referência rápida de comandos frequentes."""
        HelpSystem.print_header("REFERÊNCIA RÁPIDA - COMANDOS FREQUENTES")

        workflows = {
            "Processar nova ideia": [
                "$ brain add 'Sua ideia aqui'",
                "$ brain index",
            ],
            "Buscar informação": [
                "$ brain search 'termo de busca'",
            ],
            "Criar e testar skill": [
                "$ brain skills new minha_skill --goal 'Objetivo'",
                "$ brain skills run minha_skill --target vault/notes/",
                "$ brain skills show minha_skill",
            ],
            "Avaliar skill": [
                "$ brain eval --eval-set tests/eval.json --skill minha_skill",
                "$ brain improve --skill minha_skill --analysis analysis.json",
            ],
            "Modo autônomo": [
                "$ brain autonomous --max-cycles 10",
            ],
        }

        for workflow, commands in workflows.items():
            HelpSystem.print_section(workflow)
            for cmd in commands:
                print(f"  {cmd}")

        HelpSystem._print_usage_tips()

    @staticmethod
    def print_examples() -> None:
        """Exibe guia com exemplos práticos."""
        HelpSystem.print_header("GUIA DE EXEMPLOS PRÁTICOS")

        examples = [
            {
                "title": "1. Começar com uma nova nota",
                "steps": [
                    "brain add 'Aprendi sobre permissões em Linux'",
                    "brain index  # Indexar no RAG",
                ],
            },
            {
                "title": "2. Buscar conteúdo no vault",
                "steps": [
                    "brain search 'permissões de arquivo'",
                    "# Retorna notas relacionadas",
                ],
            },
            {
                "title": "3. Criar uma nova skill",
                "steps": [
                    "brain skills new classificador_markdown --goal 'Classificar markdown'",
                    "brain skills show classificador_markdown  # Ver template",
                    "# Editar o arquivo SKILL.md",
                ],
            },
            {
                "title": "4. Testar uma skill",
                "steps": [
                    "brain skills run classificador_markdown --target vault/notes/",
                    "# Usar --dry-run para ver prompt sem executar",
                    "brain skills run classificador_markdown --target vault/notes/ --dry-run",
                ],
            },
            {
                "title": "5. Avaliar performance de skill",
                "steps": [
                    "brain eval --eval-set tests/skill_eval.json --skill classificador_markdown",
                    "# Ver relatório de métricas",
                ],
            },
            {
                "title": "6. Melhorar uma skill",
                "steps": [
                    "# Após avaliação, gerar análise",
                    "brain improve --skill classificador_markdown --analysis analysis.json",
                    "# Nova versão salva em skills/classificador_markdown/v2/",
                ],
            },
            {
                "title": "7. Modo autônomo",
                "steps": [
                    "brain autonomous --max-cycles 5",
                    "# Sistema executa ciclos autônomos com melhorias automáticas",
                ],
            },
        ]

        for example in examples:
            HelpSystem.print_section(example["title"])
            for step in example["steps"]:
                print(f"  {step}")

        HelpSystem._print_usage_tips()


def cmd_help(args: Any) -> int:
    """Comando 'brain help' para exibir ajuda."""
    command = getattr(args, "command_name", None)

    if command:
        HelpSystem.print_command_help(command)
    elif getattr(args, "list", False):
        HelpSystem.print_command_list()
    elif getattr(args, "quick", False):
        HelpSystem.print_quick_reference()
    elif getattr(args, "examples", False):
        HelpSystem.print_examples()
    else:
        HelpSystem.print_command_list()

    return 0

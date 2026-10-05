# Second Brain System

Sistema pessoal em Python para organizar notas em Markdown, recuperar conhecimento por busca semântica e executar tarefas com modelos de linguagem.

**Estado:** protótipo funcional, com desenvolvimento pausado por limitações de recursos para inferência local e APIs pagas. Ainda precisa de refinamento; não é um serviço de produção.

## O que foi desenvolvido

- CLI para criar, organizar, indexar e pesquisar notas.
- Recuperação semântica com LlamaIndex, ChromaDB e embeddings via Ollama.
- Integração com modelos locais e cliente Gemini para processamento de conteúdo.
- Execução de skills locais, com contexto recuperado e registros de execução.
- Dashboard experimental em Streamlit. A interface mantém notas em sessão e ainda não integra todo o fluxo persistente da CLI.

O projeto demonstra integração de componentes de IA, organização de dados e automação em Python. Os clientes legados de OpenAI e Claude precisam de revisão de compatibilidade antes de uso.

## Começar

Requer Python 3.12 ou superior e [uv](https://docs.astral.sh/uv/getting-started/installation/). Execute os comandos na raiz do projeto:

```bash
git clone https://github.com/JonasChristiano/second_brain_system.git
cd second_brain_system
uv sync --locked
uv run python brain --help
```

A configuração de modelos, embeddings e diretórios está no [guia de instalação](docs/INSTALLATION.md).

```bash
uv run python brain add "Uma nota sobre integração de sistemas" --model ollama:qwen3:4b
uv run python brain index
uv run python brain search "integração de sistemas" --top-k 5
uv run python brain skills list
```

Os três primeiros comandos dependem dos modelos e serviços configurados. O dashboard pode ser aberto separadamente com `uv run streamlit run dashboard.py`.

## Estrutura

| Caminho | Responsabilidade |
| --- | --- |
| `brain` | Entrada da CLI |
| `src/brain_system/` | Notas, busca, clientes de modelos e orquestração |
| `skills/` | Definições locais de tarefas |
| `dashboard.py` | Interface experimental |
| `tests/` | Testes automatizados |
| `docs/` | Documentação complementar |

Por padrão, o vault fica em `vault/`, o índice em `.chroma/` e o contexto em `.codex/context.md`. As variáveis `BRAIN_ROOT` e `BRAIN_VAULT_DIR` permitem ajustar os caminhos.

## Limitações e próximos passos

- O desempenho depende do hardware, dos modelos escolhidos e dos limites das APIs.
- A qualidade das respostas precisa de avaliação por tarefa; não há garantia de exatidão.
- Notas e prompts podem aparecer nos registros de execução. Revise os dados antes de compartilhá-los ou enviá-los a um provedor externo.
- Permanecem pendentes a integração do dashboard, a revisão dos clientes legados e o refinamento da experiência de uso.

Os testes não substituem uma validação completa com serviços reais de IA. Consulte a licença e os arquivos do repositório para detalhes do código.

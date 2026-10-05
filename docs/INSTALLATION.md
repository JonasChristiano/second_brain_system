# Instalação e configuração

Este guia se refere ao código deste repositório. Não pressupõe um pacote publicado no PyPI nem caminhos específicos do computador do autor.

## Ambiente Python

Requer Python 3.12 ou superior e [uv](https://docs.astral.sh/uv/getting-started/installation/). Na raiz do clone:

```bash
uv sync --locked
uv run python brain --help
```

O `uv` cria o ambiente virtual e instala as dependências do `uv.lock`. Não é necessário ativá-lo para executar os comandos com `uv run`.

## Embeddings e busca semântica

A busca usa embeddings via Ollama, inclusive quando o processamento de notas usa uma API externa. Com Ollama instalado e o serviço local ativo:

```bash
ollama pull mxbai-embed-large:latest
export OLLAMA_EMBED_MODEL='mxbai-embed-large:latest'
```

O endereço padrão é `http://localhost:11434`. A configuração do índice está em `src/brain_system/rag.py`.

## Processamento com modelo local

```bash
ollama pull qwen3:4b
uv run python brain add "Minha primeira nota" --model ollama:qwen3:4b
```

Escolha um modelo compatível com os recursos disponíveis. `--timeout` ajusta o tempo limite do comando `add`.

## Processamento com Gemini

Configure `GEMINI_API_KEY` ou `GOOGLE_API_KEY` no ambiente, ou em um arquivo local `.env`, que já está ignorado pelo Git. Não publique a chave. `GEMINI_MODEL` permite escolher o modelo, e `BRAIN_MODEL` seleciona o cliente para os fluxos que usam essa variável.

```bash
uv run python brain add "Minha primeira nota" --model gemini
```

A chave, o modelo e a disponibilidade da API precisam ser válidos. Esse fluxo pode gerar custos. Os clientes OpenAI e Claude usam interfaces legadas e precisam de atualização antes de serem considerados alternativas compatíveis.

## Comandos básicos

```bash
uv run python brain index
uv run python brain search "Minha primeira nota" --top-k 5
uv run python brain skills list
uv run python brain skills new exemplo --goal "Organizar uma nota"
```

Use `uv run python brain <comando> --help` para consultar as opções atuais. `BRAIN_ROOT` altera a raiz de dados; `BRAIN_VAULT_DIR` altera o vault. Execute a CLI a partir da raiz do projeto para usar os caminhos padrão.

## Dashboard experimental

```bash
uv run streamlit run dashboard.py
```

A interface usa estado de sessão e ainda não substitui o armazenamento e a busca da CLI.

## Verificação

```bash
uv run python -m unittest discover -s tests -v
```

Há testes com dependências simuladas. A aprovação deles não demonstra disponibilidade de provedores, qualidade de respostas ou funcionamento de todos os modelos em hardware real.

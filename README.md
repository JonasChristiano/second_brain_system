# Brain System

Sistema local para organizar notas, aplicar skills de IA e consultar uma base de conhecimento em `vault/notes`.

## Estrutura

- `brain`: ponto de entrada da CLI
- `src/brain_system/`: logica principal do projeto
- `.codex/context.md`: contexto global do sistema
- `.codex/skills/*.md`: skills locais em Markdown
- `rag/`: wrappers simples para indexacao e busca
- `vault/`: notas e anexos em um Git separado

## Organizacao atual

- `src/brain_system/cli.py`: comandos da CLI
- `src/brain_system/skills.py`: leitura e composicao de prompts de skills
- `src/brain_system/vault_watch.py`: auto-commit do vault
- `src/brain_system/rag.py`: indexacao e busca vetorial
- `src/brain_system/paths.py`: caminhos centrais do projeto

## Uso rapido

```bash
python3 brain skills list
python3 brain skills show brain_orchestrator
python3 brain skills new resumo_tecnico --goal "Resumir notas tecnicas com clareza"
python3 brain skills run note_refinement --target vault/notes --instruction "Refinar notas mantendo os links"
python3 brain add "Skill de IA define um comportamento reutilizavel"
python3 brain index
python3 brain search "o que e skill de IA?"
python3 brain refine
python3 brain refine vault/notes/comando-cat.md
python3 brain restructure
python3 brain watch
```

## Testes

```bash
python3 -m unittest discover -s tests -v
python3 tests/check_coverage.py
```

O segundo comando valida cobertura de 100% nos arquivos de codigo do projeto.

## Fluxo sugerido

1. Criar ou ajustar uma skill em `.codex/skills`.
2. Executar a skill com `python3 brain skills run ...`.
3. Quando houver novas notas, reconstruir o indice com `python3 brain index`.
4. Consultar o conhecimento com `python3 brain search ...`.
5. Ao importar um vault real, executar `python3 brain restructure`.
6. Se quiser commits automaticos no vault, manter `python3 brain watch` em execucao.

## Formato de skill

As skills seguem um formato simples em Markdown:

```md
id: nome_da_skill
title: Nome da Skill
version: 1.0
last_updated: 2026-04-23
scope: vault/notes

Objetivo:
- descrever o que a skill faz

Quando usar:
- descrever os cenarios de ativacao

Passos:
1. descrever a sequencia principal

Regras:
- definir comportamento
- indicar limites
- explicar o formato de saida

Saida esperada:
- descrever o resultado final
```

O `brain` combina automaticamente o contexto global, a skill selecionada e a instrucao passada no terminal antes de chamar o `codex`.

## Auto-commit do vault

O comando `python3 brain watch` monitora o diretorio `vault/` e cria commits locais automaticamente no repositorio Git interno dessa pasta.
Ele considera criacao, edicao, renomeacao e delecao de arquivos, ignorando apenas o conteudo interno de `vault/.git/`.

## Reestruturacao do vault

O comando `python3 brain restructure` prepara um vault existente para a estrutura padrao do projeto.
Ele garante as pastas `notes/`, `attachments/`, `templates/`, `inbox/` e `archive/`, move arquivos Markdown soltos para `notes/` e move outros anexos para `attachments/`.
Pastas ja estruturadas e o conteudo interno de `vault/.git/` sao preservados.

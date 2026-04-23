# Brain System

Sistema local para organizar notas, aplicar skills de IA e consultar uma base de conhecimento em `vault/notes`.

## Estrutura

- `brain`: CLI principal para skills, captura de ideias e RAG
- `.codex/context.md`: contexto global do sistema
- `.codex/skills/*.md`: skills locais em Markdown
- `vault/notes`: notas do vault
- `rag/`: indexacao e busca vetorial

## Uso rapido

```bash
python3 brain skills list
python3 brain skills show brain_orchestrator
python3 brain skills new resumo_tecnico --goal "Resumir notas tecnicas com clareza"
python3 brain skills run note_refinement --target vault/notes --instruction "Refinar notas mantendo os links"
python3 brain add "Skill de IA define um comportamento reutilizavel"
python3 brain index
python3 brain search "o que e skill de IA?"
```

## Fluxo sugerido

1. Criar ou ajustar uma skill em `.codex/skills`.
2. Executar a skill com `python3 brain skills run ...`.
3. Quando houver novas notas, reconstruir o indice com `python3 brain index`.
4. Consultar o conhecimento com `python3 brain search ...`.

## Formato de skill

As skills seguem um formato simples em Markdown:

```md
id="nome_da_skill"

Objetivo:
- descrever o que a skill faz

Regras:
- definir comportamento
- indicar limites
- explicar o formato de saida
```

O `brain` combina automaticamente o contexto global, a skill selecionada e a instrucao passada no terminal antes de chamar o `codex`.

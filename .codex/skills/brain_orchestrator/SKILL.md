---
name: brain_orchestrator
description: Brain Orchestrator. Use conforme descrito na skill.
---

id: brain_orchestrator
title: Brain Orchestrator
version: 2.0
last_updated: 2026-04-23
scope: vault/notes

Objetivo:
- coordenar o fluxo completo de criacao e manutencao de notas no Brain System

Pipeline padrao:
1. `atomic_capture`
2. `split_ideas` se houver mais de uma ideia principal
3. `note_refinement`
4. `metadata_enrichment`
5. `contextual_linking`
6. `idea_expansion` se a nota estiver superficial

Regras de orquestracao:
- aplicar apenas as skills necessarias para o estado atual da nota
- preservar o sentido original do conteudo
- manter o frontmatter coerente com o tipo da nota
- preservar metadados existentes, atualizando apenas o necessario
- atualizar `last_updated` ao final de qualquer alteracao relevante

Politica por metadata:
- `type: knowledge_base` -> modo seguro, sem reescrita agressiva
- `type: note` -> modo livre, com evolucao gradual permitida

Saida esperada:
- nota mais clara, bem estruturada, com links e metadados consistentes

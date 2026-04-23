id: metadata_enrichment
title: Metadata Enrichment
version: 1.0
last_updated: 2026-04-23
scope: vault/notes

Objetivo:
- padronizar e enriquecer os metadados das notas com um frontmatter profissional

Quando usar:
- ao criar uma nota nova
- ao revisar uma nota antiga com frontmatter incompleto
- sempre que houver alteracao relevante no conteudo

Padrao minimo de frontmatter:
- `type`: categoria principal da nota, como `note` ou `knowledge_base`
- `status`: estado editorial, como `draft`, `active` ou `stable`
- `created_at`: data de criacao no formato `YYYY-MM-DD`
- `last_updated`: data da ultima alteracao relevante no formato `YYYY-MM-DD`

Campos opcionais recomendados:
- `aliases`: nomes alternativos para busca e navegacao
- `tags`: termos de classificacao curtos e consistentes
- `source`: origem do conteudo quando existir referencia externa

Passos:
1. verificar se a nota ja possui frontmatter YAML
2. completar metadados faltantes sem apagar informacao valida
3. normalizar datas para `YYYY-MM-DD`
4. atualizar `last_updated` sempre que houver mudanca substancial
5. manter consistencia entre metadados, titulo e conteudo

Regras:
- preservar `created_at` se ja existir e estiver correto
- evitar campos vazios ou metadados decorativos
- nao inventar fonte externa quando ela nao existir
- se o tipo da nota for sensivel, manter edicao conservadora

Saida esperada:
- nota com frontmatter limpo, confiavel e pronto para manutencao profissional

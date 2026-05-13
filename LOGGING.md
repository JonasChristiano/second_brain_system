# 📋 Guia de Logging do Brain System

## Configuração

Para habilitar logging na aplicação, adicione no ponto de entrada:

```python
from brain_system import setup_logging
import logging

# Configurar logging no início da aplicação
setup_logging(level=logging.DEBUG, detailed=True)  # Para debug
# ou
setup_logging(level=logging.INFO)  # Para produção
```

## Uso em Módulos

Em cada módulo, adicione no início:

```python
import logging
logger = logging.getLogger(__name__)
```

## Níveis de Log Recomendados

| Nível | Quando Usar | Exemplo |
|-------|-------------|---------|
| `DEBUG` | Detalhes de execução, valores de variáveis | `logger.debug(f"Parâmetros: {params}")` |
| `INFO` | Eventos importantes, início/fim de operações | `logger.info("[MODULO] Operação iniciada")` |
| `WARNING` | Situações anormais, fallbacks | `logger.warning("[MODULO] Usando fallback")` |
| `ERROR` | Erros tratáveis | `logger.error("[MODULO] Erro ao processar", exc_info=True)` |
| `CRITICAL` | Falhas graves do sistema | `logger.critical("[MODULO] Sistema indisponível")` |

## Padrão de Mensagens

Use o formato `[MODULO] mensagem descritiva`:

```python
# ✅ Bom
logger.info("[LLM] Consulta iniciada")
logger.error("[RAG] Índice corrompido", exc_info=True)
logger.debug("[CLI] Argumentos: {args}")

# ❌ Evitar
logger.info("iniciado")
logger.error("erro")
logger.debug("processando...")
```

## Exemplos Implementados

### llm_adapter.py
- `[LLM] Iniciando consulta` com modelo
- `[LLM] Resposta concluída com sucesso`
- `[LLM] Erro na consulta` com stack trace

### rag.py
- `[RAG] Configurando embeddings`
- `[RAG] Iniciando construção do índice`
- `[RAG] Iniciando busca`

### cli.py
- `[CLI] Comando 'add' iniciado`
- `[CLI] Nota adicionada com sucesso`
- `[CLI] Usando pipeline legado`

### vault_watch.py
- `[VAULT] Verificando repositório`
- `[VAULT] Mudanças detectadas`
- `[VAULT] Commit realizado`

### agents/executor.py
- `[SKILL] Executando skill`
- `[SKILL] Buscando contexto RAG`
- `[SKILL] Resposta recebida`

### skills.py
- `[SKILLS] Carregando skill`
- `[SKILLS] Listando skills`

## Arquivos de Log

Os logs são salvos em: `./logs/brain_system.log`

Para visualizar logs em tempo real:
```bash
tail -f logs/brain_system.log
```

Para debug detalhado:
```bash
grep "\[MODULO\]" logs/brain_system.log
```

## Dicas para Debug

1. **Buscar logs de um módulo específico:**
   ```bash
   grep "\[RAG\]" logs/brain_system.log
   ```

2. **Ver apenas erros e avisos:**
   ```bash
   grep "ERROR\|WARNING" logs/brain_system.log
   ```

3. **Ver últimas N linhas:**
   ```bash
   tail -n 100 logs/brain_system.log
   ```

4. **Análise de performance (tempo de execução):**
   - Procure por mensagens com duração (ex: "recebida em 2.34s")
   - Compare tempos de diferentes operações

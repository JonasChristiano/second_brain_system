"""
Configuração centralizada de logging para o Brain System.

Fornece setup de logging com formato consistente e níveis apropriados
para facilitar debugging e monitoramento do sistema.
"""

import logging
import sys
from pathlib import Path

# Criar diretório de logs se não existir
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Formato padrão para logs
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FORMAT_DETAILED = (
    "%(asctime)s - [%(filename)s:%(lineno)d] - %(name)s - %(levelname)s - %(message)s"
)


def setup_logging(
    level: int = logging.INFO,
    log_file: str | None = None,
    detailed: bool = False,
) -> None:
    """
    Configura logging para toda a aplicação.

    Args:
        level: Nível de logging (padrão: INFO)
        log_file: Arquivo para salvar logs (padrão: logs/brain_system.log)
        detailed: Se True, usa formato detalhado com nome de arquivo e linha
    """
    log_format = LOG_FORMAT_DETAILED if detailed else LOG_FORMAT
    formatter = logging.Formatter(log_format)

    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remover handlers existentes para evitar duplicação
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Handler para arquivo (se especificado)
    if log_file is None:
        log_file = str(LOGS_DIR / "brain_system.log")

    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Sempre salvar DEBUG no arquivo
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        print(f"Logs sendo salvos em: {log_file}")
    except Exception as e:
        print(f"Aviso: Não foi possível criar handler de arquivo: {e}")


def get_logger(name: str) -> logging.Logger:
    """Obtém logger para um módulo específico."""
    return logging.getLogger(name)

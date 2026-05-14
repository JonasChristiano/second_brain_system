from __future__ import annotations

import subprocess
import time
import logging
from pathlib import Path

from .paths import VAULT_DIR, VAULT_GIT_DIR

logger = logging.getLogger(__name__)

SCAN_INTERVAL = 2.0


def git(args: list[str]) -> subprocess.CompletedProcess[str]:
    logger.debug(f"[VAULT] Executando git: {' '.join(args)}")
    return subprocess.run(
        ["git", "-C", str(VAULT_DIR), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def ensure_vault_repo() -> None:
    logger.info("[VAULT] Verificando se repositório Git está inicializado")
    if not VAULT_GIT_DIR.exists():
        logger.error("[VAULT] Repositório Git não encontrado")
        raise SystemExit(
            "O diretorio vault nao possui um repositorio Git inicializado."
        )


def snapshot_vault() -> dict[str, tuple[int, int]]:
    logger.debug(f"[VAULT] Criando snapshot de {VAULT_DIR}")
    snapshot: dict[str, tuple[int, int]] = {}

    for path in VAULT_DIR.rglob("*"):
        if not path.is_file():
            continue
        if VAULT_GIT_DIR in path.parents:
            continue

        stat = path.stat()
        relative_path = str(path.relative_to(VAULT_DIR))
        snapshot[relative_path] = (stat.st_mtime_ns, stat.st_size)

    logger.debug(f"[VAULT] Snapshot concluído: {len(snapshot)} arquivos")
    return snapshot


def describe_changes(
    previous: dict[str, tuple[int, int]],
    current: dict[str, tuple[int, int]],
) -> list[str]:
    created = sorted(current.keys() - previous.keys())
    deleted = sorted(previous.keys() - current.keys())
    modified = sorted(
        path
        for path in (current.keys() & previous.keys())
        if current[path] != previous[path]
    )

    changes = created + modified + deleted
    logger.debug(
        f"[VAULT] Mudanças detectadas: {len(created)} criadas, {len(modified)} modificadas, {len(deleted)} deletadas"
    )
    return changes


def build_commit_message(paths: list[str]) -> str:
    preview = ", ".join(paths[:3])
    if len(paths) > 3:
        preview += f" e mais {len(paths) - 3}"
    return f"Auto-commit vault: {preview}"


def commit_changes(paths: list[str]) -> None:
    logger.info(f"[VAULT] Iniciando commit de mudanças: {len(paths)} arquivo(s)")
    logger.debug(f"[VAULT] Arquivos: {paths[:5]}{'...' if len(paths) > 5 else ''}")

    status = git(["status", "--short"])
    if status.returncode != 0:
        logger.error(f"[VAULT] Erro ao consultar status: {status.stderr}")
        print(status.stderr.strip() or "Falha ao consultar o status do vault.")
        return

    if not status.stdout.strip():
        logger.debug("[VAULT] Nenhuma mudança pendente")
        return

    add_result = git(["add", "-A"])
    if add_result.returncode != 0:
        logger.error(f"[VAULT] Erro ao adicionar mudanças: {add_result.stderr}")
        print(add_result.stderr.strip() or "Falha ao adicionar mudancas do vault.")
        return

    commit_result = git(["commit", "-m", build_commit_message(paths)])
    if commit_result.returncode == 0:
        logger.info(f"[VAULT] Commit realizado com sucesso")
        print(commit_result.stdout.strip())
        return

    logger.error(
        f"[VAULT] Erro ao criar commit: {commit_result.stderr or commit_result.stdout}"
    )
    print(
        commit_result.stderr.strip()
        or commit_result.stdout.strip()
        or "Falha ao criar auto-commit do vault."
    )


def main() -> None:
    logger.info("[VAULT] Iniciando monitoramento do vault")
    ensure_vault_repo()

    previous_snapshot = snapshot_vault()
    print("Vault auto-commit ativo.")
    print(f"Monitorando {VAULT_DIR}")

    try:
        while True:
            time.sleep(SCAN_INTERVAL)
            current_snapshot = snapshot_vault()
            changed_paths = describe_changes(previous_snapshot, current_snapshot)

            if not changed_paths:
                continue

            logger.info(
                f"[VAULT] Mudanças detectadas, processando {len(changed_paths)} arquivo(s)"
            )
            commit_changes(changed_paths)
            previous_snapshot = snapshot_vault()
    except KeyboardInterrupt:
        logger.info("[VAULT] Monitoramento encerrado pelo usuário")
        print("\nWatcher encerrado.")

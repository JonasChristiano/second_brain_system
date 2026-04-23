from __future__ import annotations

import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VAULT_DIR = ROOT / "vault"
VAULT_GIT_DIR = VAULT_DIR / ".git"
SCAN_INTERVAL = 2.0


def git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(VAULT_DIR), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def ensure_vault_repo() -> None:
    if not VAULT_GIT_DIR.exists():
        raise SystemExit("O diretorio vault nao possui um repositorio Git inicializado.")


def snapshot_vault() -> dict[str, tuple[int, int]]:
    snapshot: dict[str, tuple[int, int]] = {}

    for path in VAULT_DIR.rglob("*"):
        if not path.is_file():
            continue
        if VAULT_GIT_DIR in path.parents:
            continue

        stat = path.stat()
        relative_path = str(path.relative_to(VAULT_DIR))
        snapshot[relative_path] = (stat.st_mtime_ns, stat.st_size)

    return snapshot


def describe_changes(previous: dict[str, tuple[int, int]], current: dict[str, tuple[int, int]]) -> list[str]:
    created = sorted(current.keys() - previous.keys())
    deleted = sorted(previous.keys() - current.keys())
    modified = sorted(
        path
        for path in (current.keys() & previous.keys())
        if current[path] != previous[path]
    )

    return created + modified + deleted


def build_commit_message(paths: list[str]) -> str:
    preview = ", ".join(paths[:3])
    if len(paths) > 3:
        preview += f" e mais {len(paths) - 3}"
    return f"Auto-commit vault: {preview}"


def commit_changes(paths: list[str]) -> None:
    status = git(["status", "--short"])
    if status.returncode != 0:
        print(status.stderr.strip() or "Falha ao consultar o status do vault.")
        return

    if not status.stdout.strip():
        return

    add_result = git(["add", "-A"])
    if add_result.returncode != 0:
        print(add_result.stderr.strip() or "Falha ao adicionar mudancas do vault.")
        return

    commit_result = git(["commit", "-m", build_commit_message(paths)])
    if commit_result.returncode == 0:
        print(commit_result.stdout.strip())
        return

    print(commit_result.stderr.strip() or commit_result.stdout.strip() or "Falha ao criar auto-commit do vault.")


def main() -> None:
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

            commit_changes(changed_paths)
            previous_snapshot = snapshot_vault()
    except KeyboardInterrupt:
        print("\nWatcher encerrado.")


if __name__ == "__main__":
    main()

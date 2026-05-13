from __future__ import annotations

import dis
import sys
import trace
import unittest
from pathlib import Path
from types import CodeType


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

for path in (ROOT, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

TARGETS = [
    ROOT / "brain",
    ROOT / "dashboard.py",
    ROOT / "rag" / "indexer.py",
    ROOT / "rag" / "search.py",
    ROOT / "restructure.py",
    ROOT / "whatcher.py",
    ROOT / "src" / "brain_system" / "__init__.py",
    ROOT / "src" / "brain_system" / "cli.py",
    ROOT / "src" / "brain_system" / "paths.py",
    ROOT / "src" / "brain_system" / "rag.py",
    ROOT / "src" / "brain_system" / "skills.py",
    ROOT / "src" / "brain_system" / "llm" / "client.py",
    ROOT / "src" / "brain_system" / "help.py",
    ROOT / "src" / "brain_system" / "vault_watch.py",
]


def iter_code_objects(code: CodeType) -> list[CodeType]:
    nested = [code]
    for const in code.co_consts:
        if isinstance(const, CodeType):
            nested.extend(iter_code_objects(const))
    return nested


def executable_lines(path: Path) -> set[int]:
    source = path.read_text(encoding="utf-8")
    code = compile(source, str(path), "exec")
    executable: set[int] = set()

    for code_obj in iter_code_objects(code):
        executable.update(
            line
            for _, line in dis.findlinestarts(code_obj)
            if line is not None and line > 0
        )

    return executable


def executed_lines(results: trace.CoverageResults, path: Path) -> set[int]:
    resolved = str(path.resolve())
    return {
        line
        for (filename, line), _count in results.counts.items()
        if filename == resolved
    }


def main() -> int:
    tracer = trace.Trace(count=True, trace=False)

    def run_tests() -> None:
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
        result = unittest.TextTestRunner(verbosity=0).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)

    tracer.runfunc(run_tests)

    results = tracer.results()
    missing_any = False

    for target in TARGETS:
        executable = executable_lines(target)
        executed = executed_lines(results, target)
        missing = sorted(executable - executed)

        if missing:
            missing_any = True
            print(f"FALHA {target.relative_to(ROOT)} sem cobertura total: {missing}")
        else:
            print(f"OK {target.relative_to(ROOT)} 100%")

    return 1 if missing_any else 0


if __name__ == "__main__":
    raise SystemExit(main())

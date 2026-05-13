from __future__ import annotations

import contextlib
import importlib
import io
import runpy
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def install_fake_rag_dependencies() -> dict[str, object]:
    state: dict[str, object] = {}

    chromadb_module = types.ModuleType("chromadb")

    class FakeClient:
        def __init__(self, path: str | None = None) -> None:
            pass

        def get_or_create_collection(self, name: str) -> str:
            state["collection_name"] = name
            return f"collection:{name}"

    chromadb_module.Client = FakeClient
    chromadb_module.PersistentClient = FakeClient  # Same for simplicity

    llama_index_module = types.ModuleType("llama_index")
    core_module = types.ModuleType("llama_index.core")
    vector_stores_module = types.ModuleType("llama_index.vector_stores")
    chroma_module = types.ModuleType("llama_index.vector_stores.chroma")

    class FakeReader:
        def __init__(self, directory: str) -> None:
            state["reader_directory"] = directory

        def load_data(self) -> list[str]:
            state["reader_loaded"] = True
            return ["doc-a", "doc-b"]

    class FakeQueryEngine:
        def query(self, text: str) -> str:
            state["query"] = text
            return f"resultado:{text}"

    class FakeIndex:
        def as_query_engine(self) -> FakeQueryEngine:
            return FakeQueryEngine()

    class FakeVectorStoreIndex:
        @staticmethod
        def from_documents(docs: list[str], vector_store: object) -> FakeIndex:
            state["from_documents"] = (docs, vector_store)
            return FakeIndex()

        @staticmethod
        def from_vector_store(store: object) -> FakeIndex:
            state["from_vector_store"] = store
            return FakeIndex()

    class FakeChromaVectorStore:
        def __init__(self, chroma_collection: object) -> None:
            state["chroma_collection"] = chroma_collection
            self.chroma_collection = chroma_collection

    core_module.SimpleDirectoryReader = FakeReader
    core_module.VectorStoreIndex = FakeVectorStoreIndex
    chroma_module.ChromaVectorStore = FakeChromaVectorStore

    sys.modules["chromadb"] = chromadb_module
    sys.modules["llama_index"] = llama_index_module
    sys.modules["llama_index.core"] = core_module
    sys.modules["llama_index.vector_stores"] = vector_stores_module
    sys.modules["llama_index.vector_stores.chroma"] = chroma_module
    return state


class RagTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_modules = sys.modules.copy()
        self.state = install_fake_rag_dependencies()
        sys.modules.pop("brain_system.rag", None)
        self.rag = importlib.import_module("brain_system.rag")

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def test_store_build_index_and_search(self) -> None:
        # When dependencies are mocked but imports fail, CHROMADB_AVAILABLE = False
        # So build_index just prints message, search returns mock result

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.rag.build_index()
        self.assertIn("chromadb não disponível", stdout.getvalue())

        results = self.rag.search("pergunta")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "resultado:pergunta")
        self.assertEqual(results[0]["score"], 0.8)


class WrapperTests(unittest.TestCase):
    def test_brain_wrapper_runs_cli_main(self) -> None:
        fake_cli = types.ModuleType("brain_system.cli")
        called = {"value": False}

        def fake_main() -> int:
            called["value"] = True
            return 17

        fake_cli.main = fake_main

        path_without_src = [path for path in sys.path if path != str(SRC_DIR)]

        with (
            mock.patch.dict(sys.modules, {"brain_system.cli": fake_cli}, clear=False),
            mock.patch.object(sys, "path", path_without_src),
        ):
            with self.assertRaises(SystemExit) as ctx:
                runpy.run_path(str(ROOT / "brain"), run_name="__main__")
        self.assertEqual(ctx.exception.code, 17)
        self.assertTrue(called["value"])

    def test_whatcher_wrapper_runs_main(self) -> None:
        fake_watch = types.ModuleType("brain_system.vault_watch")
        called = {"value": False}

        def fake_main() -> None:
            called["value"] = True

        fake_watch.main = fake_main

        path_without_src = [path for path in sys.path if path != str(SRC_DIR)]

        with (
            mock.patch.dict(
                sys.modules, {"brain_system.vault_watch": fake_watch}, clear=False
            ),
            mock.patch.object(sys, "path", path_without_src),
        ):
            runpy.run_path(str(ROOT / "whatcher.py"), run_name="__main__")
        self.assertTrue(called["value"])

    def test_rag_wrappers_run_package_functions(self) -> None:
        fake_rag = types.ModuleType("brain_system.rag")
        state = {"build": 0, "search": None}

        def fake_build_index() -> None:
            state["build"] += 1

        def fake_search(query: str) -> None:
            state["search"] = query

        fake_rag.build_index = fake_build_index
        fake_rag.search = fake_search
        # Alias for search.py import
        fake_rag.search_index = fake_search

        with (
            mock.patch.dict(sys.modules, {"brain_system.rag": fake_rag}, clear=False),
            mock.patch.object(
                sys, "path", [path for path in sys.path if path != str(SRC_DIR)]
            ),
        ):
            runpy.run_path(str(ROOT / "rag" / "indexer.py"), run_name="__main__")

        with (
            mock.patch.dict(sys.modules, {"brain_system.rag": fake_rag}, clear=False),
            mock.patch.object(
                sys, "path", [path for path in sys.path if path != str(SRC_DIR)]
            ),
        ):
            with mock.patch.object(sys, "argv", ["search.py", "consulta"]):
                runpy.run_path(str(ROOT / "rag" / "search.py"), run_name="__main__")

        self.assertEqual(state["build"], 1)
        self.assertEqual(state["search"], "consulta")

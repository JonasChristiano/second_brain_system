from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from brain_system.paths import NOTES_DIR

st.title("🧠 Brain Dashboard")

files = sorted(path.name for path in NOTES_DIR.glob("*.md"))

st.metric("Notas totais", len(files))

search = st.text_input("Buscar")

for f in files:
    if search.lower() in f.lower():
        st.write(f)

import streamlit as st
import uuid
import logging
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)
logger.info("[DASHBOARD] Iniciando aplicação")

st.set_page_config(layout="wide")

# ─── THEME ─────────────────────────────────────────

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Oxanium:wght@600&display=swap');

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: #080c08;
    color: #d1fae5;
}

[data-testid="stSidebar"] {
    background-color: #0e130e;
    border-right: 1px solid #1c281c;
}

.card {
    background: #121a12;
    border: 1px solid #1c281c;
    padding: 10px;
    margin-bottom: 8px;
}

.title {
    font-family: 'Oxanium';
    color: #4ade80;
    font-size: 18px;
    font-weight: bold;
}

.tag {
    background: #16653422;
    border: 1px solid #166534;
    padding: 2px 6px;
    font-size: 10px;
    margin-right: 4px;
}

button[kind="primary"] {
    background-color: transparent;
    border: 1px solid #4ade80;
    color: #4ade80;
}
</style>
""",
    unsafe_allow_html=True,
)

# ─── STATE ─────────────────────────────────────────

if "notes" not in st.session_state:
    st.session_state.notes = []

if "view" not in st.session_state:
    st.session_state.view = "new"

if "selected" not in st.session_state:
    st.session_state.selected = None

# ─── HELPERS ───────────────────────────────────────


def create_note(raw):
    return {
        "id": str(uuid.uuid4()),
        "title": raw[:40],
        "summary": raw[:80],
        "content": raw,
        "tags": ["note"],
        "created": datetime.now().isoformat(),
        "version": 1,
    }


# ─── SIDEBAR ───────────────────────────────────────

st.sidebar.markdown("## SBS")
st.sidebar.markdown("Second Brain System")

search = st.sidebar.text_input("Search")

if st.sidebar.button("+ New Note"):
    st.session_state.view = "new"
    st.session_state.selected = None

st.sidebar.markdown("### Notes")

for note in st.session_state.notes:
    if search.lower() in note["title"].lower():
        if st.sidebar.button(note["title"], key=note["id"]):
            st.session_state.selected = note
            st.session_state.view = "note"

# ─── MAIN LAYOUT ───────────────────────────────────

left, right = st.columns([3, 1])

# ─── NEW NOTE ──────────────────────────────────────

if st.session_state.view == "new":
    with left:
        st.markdown(
            '<div class="title">/ NEW ATOMIC NOTE</div>', unsafe_allow_html=True
        )

        raw = st.text_area("Write your idea...", height=200)

        if st.button("PROCESS NOTE"):
            if raw:
                note = create_note(raw)
                st.session_state.notes.insert(0, note)
                st.session_state.selected = note
                st.session_state.view = "note"
                st.success("Note created")

# ─── VIEW NOTE ─────────────────────────────────────

if st.session_state.view == "note" and st.session_state.selected:
    note = st.session_state.selected

    with left:
        st.markdown(f'<div class="title">{note["title"]}</div>', unsafe_allow_html=True)
        st.write(note["summary"])

        st.markdown("### Content")
        st.markdown(note["content"])

        col1, col2, col3 = st.columns(3)

        if col1.button("Improve"):
            note["content"] += "\n\n💡 Improved"
            note["version"] += 1

        if col2.button("Delete"):
            st.session_state.notes = [
                n for n in st.session_state.notes if n["id"] != note["id"]
            ]
            st.session_state.view = "new"
            st.session_state.selected = None

        if col3.button("Edit"):
            st.session_state.view = "edit"

# ─── EDIT ──────────────────────────────────────────

if st.session_state.view == "edit":
    note = st.session_state.selected

    with left:
        title = st.text_input("Title", note["title"])
        content = st.text_area("Content", note["content"], height=300)

        if st.button("Save"):
            note["title"] = title
            note["content"] = content
            note["version"] += 1
            st.session_state.view = "note"

# ─── RIGHT PANEL ───────────────────────────────────

with right:
    st.markdown("### Intelligence")

    total_notes = len(st.session_state.notes)

    st.markdown(f'<div class="card">Notes: {total_notes}</div>', unsafe_allow_html=True)

    avg_len = (
        sum(len(n["content"]) for n in st.session_state.notes) if total_notes else 0
    )
    st.markdown(f'<div class="card">Avg Size: {avg_len}</div>', unsafe_allow_html=True)

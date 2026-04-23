import streamlit as st
import os

NOTES = "./vault/notes"

st.title("🧠 Brain Dashboard")

files = os.listdir(NOTES)

st.metric("Notas totais", len(files))

search = st.text_input("Buscar")

for f in files:
    if search.lower() in f.lower():
        st.write(f)

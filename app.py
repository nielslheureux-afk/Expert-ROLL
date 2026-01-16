import streamlit as st
from groq import Groq
import os
import io
from docx import Document

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

# --- 2. INITIALISATION DU MOTEUR (GROQ) ---
# Assurez-vous d'avoir GROQ_API_KEY dans les Secrets de Streamlit
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.title("🤖 Expert ROLL")
    st.info("👋 Veuillez configurer la GROQ_API_KEY dans les Secrets pour commencer.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. FONCTION DE CRÉATION DU DOCUMENT WORD ---
def create_docx(text, cycle_name):
    doc = Document()
    
    # Titre principal
    doc.add_heading(f"Fiche ACT ROLL - {cycle_name}", 0)
    
    # Parcours du texte pour mise en page simple
    for line in text.split('\n'):
        clean_line = line.replace('*', '').replace('#', '').strip()
        if not clean_line:
            continue
            
        if any(word.isupper() for word in clean_line.split()[:2]) and len(clean_line) < 60:
            doc.add_heading(clean_line, level=1)
        elif line.strip().startswith(('-', '•', '*')):
            doc.add_paragraph(clean_line, style='List Bullet')
        else:
            doc.add_paragraph(clean_line)
            
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. INTERFACE UTILISATEUR ---
st.title("🤖 Expert ROLL")
st.caption("Moteur : Llama 3.3 (Stable & Rapide)")

cycle = st.radio("Niveau scolaire :", ["Cycle 2 (CP-CE2)", "Cycle 3 (CM1-6ème)"])
uploaded_file = st.file_uploader("Charger le texte (Format Word .docx)", type=['docx'])

# --- 5. GÉNÉRATION ---
if uploaded_file and st.button("🚀 Générer

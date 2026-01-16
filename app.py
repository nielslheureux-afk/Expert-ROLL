import streamlit as st
import google.generativeai as genai
import os
import io
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Expert ROLL - Fiches ACT", page_icon="📖")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. MOTEUR DE RENDU WORD INTELLIGENT ---
def create_roll_docx_faithful(text_content, cycle_name):
    doc = Document()
    doc.styles['Normal'].font.name = 'Arial'
    doc.styles['Normal'].font.size = Pt(11)

    # Titre
    title = doc.add_heading(f"FICHE ENSEIGNANT : ACT TYPE 1 - {cycle_name}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    lines = text_content.split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line: continue

        # Gestion des Titres
        if clean_line.startswith(('#', '1.', '2.', '3.', '4.')) or "PHASE" in clean_line.upper():
            doc.add_heading(clean_line.replace('#', '').strip(), level=1)
        
        # Détection et création de TABLEAU (si l'IA utilise des séparateurs | )
        elif "|" in clean_line and "---" not in clean_line:
            parts = [p.strip() for p in clean_line.split("|") if p.strip()]
            if len(parts) >= 2:
                table = doc.add_table(rows=1, cols=len(parts))
                table.style = 'Table Grid'
                for i, part in enumerate(parts):
                    table.rows[0].cells[i].text = part
        
        # Gestion du Gras
        elif '**' in clean_line:
            p = doc.add_paragraph()
            parts = clean_line.split('**')
            for i, part in enumerate(parts):
                run = p.add_run(part)
                if i % 2 != 0: run.bold = True
        
        # Listes
        elif clean_line.startswith(('-', '*', '•')):
            doc.add_paragraph(clean_line.strip('-*• ').strip(), style='List Bullet')
        
        else:
            doc.add_paragraph(clean_line)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. INTERFACE ---
st.title("🤖 Expert ROLL")
cycle = st.radio("Cycle concerné :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Support (Word, PDF ou Photo)", type=['docx', 'pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file and st.button("🚀 Générer la fiche complète"):
    with st.spinner('Construction de la fiche avec tableau pré-rempli...'):
        try:
            raw_content = ""
            file_data = None
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc_in = Document(uploaded_file)
                raw_content = "\n".join([p.text for p in doc_in.paragraphs])
            elif uploaded_file.type == "application/pdf":
                pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                raw_content = "".join([page.get_text() for page in pdf_doc])
            else:
                file_data = {"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()}

            # PROMPT AVEC DEMANDE EXPLICITE DE TABLEAU PRÉ-REMPLI
            instruction = f"""Agis en tant qu'expert pédagogique du ROLL. Rédige une fiche enseignant complète pour un ACT de type 1 (narratif) pour le {cycle}.
            Respecte scrupuleusement les 4 phases. 
            
            IMPORTANT pour la Phase 2 : 
            Génère un tableau pré-rempli pour l'enseignant avec des exemples de propositions probables des élèves, classées en 3 colonnes : 
            - "Ce qu'on sait (certitudes)"

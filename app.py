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

# --- 2. MOTEUR DE RENDU WORD AVEC VRAI TABLEAU ---
def create_roll_docx_with_table(text_content, cycle_name):
    doc = Document()
    doc.styles['Normal'].font.name = 'Arial'
    doc.styles['Normal'].font.size = Pt(11)

    # Titre
    title = doc.add_heading(f"FICHE ENSEIGNANT : ACT TYPE 1 - {cycle_name}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sections = text_content.split('\n')
    
    for line in sections:
        clean_line = line.strip()
        if not clean_line: continue

        # Gestion des Titres
        if clean_line.startswith(('#', '1.', '2.', '3.', '4.')) or "PHASE" in clean_line.upper():
            doc.add_heading(clean_line.replace('#', '').strip(), level=1)
        
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

    # --- AJOUT DU TABLEAU DE CONTROVERSE RÉEL ---
    doc.add_page_break()
    doc.add_heading("OUTIL : TABLEAU DE CONFRONTATION DES REPRÉSENTATIONS", level=2)
    
    # Création d'un tableau vide structuré (3 colonnes ROLL)
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "On est d'accord"
    hdr_cells[1].text = "On n'est pas d'accord"
    hdr_cells[2].text = "On ne sait pas"
    
    # On ajoute 6 lignes prêtes à l'emploi pour les élèves
    for _ in range(6):
        table.add_row()

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. INTERFACE ---
st.title("🤖 Expert ROLL")

cycle = st.radio("Cycle concerné :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Support (Word, PDF ou Photo)", type=['docx', 'pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file and st.button("🚀 Générer la fiche complète"):
    with st.spinner('Construction de la fiche méthodologique...'):
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

            # UTILISATION DE VOTRE PROMPT SATISFAISANT
            instruction = f"""Agis en tant qu'expert pédagogique du ROLL. Rédige une fiche enseignant complète pour un ACT de type 1 (narratif) pour le {cycle}.
            Respecte scrupuleusement les 4 phases :
            1. Identification du support.
            2. Objectifs (Habiletés ROLL : personnages, inférences).
            3. Déroulement : 
               - Phase 1 (Lecture individuelle).
               - Phase 2 (Émergence) : 3 questions ouvertes + exemples de points de controverse.
               - Phase 3 (Analyse/Vérification) : Retour au texte (lignes/mots).
               - Phase 4 (Métacognition).
            4. Prolongements.
            
            Texte : {raw_content if not file_data else 'Analyse l image jointe.'}
            """

            if file_data:
                response = model.generate_content([instruction, file_data])
            else:
                response = model.generate_content(instruction)
            
            st.markdown("---")
            st.markdown(response.text)
            
            # On génère le Word avec la nouvelle fonction de tableau
            docx_output = create_roll_docx_with_table(response.text, cycle)
            
            st.download_button(
                label="📥 Télécharger la Fiche Word (avec Tableau)",
                data=docx_output,
                file_name=f"ACT_ROLL_{cycle}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        except Exception as e:
            st.error(f"Erreur : {e}")

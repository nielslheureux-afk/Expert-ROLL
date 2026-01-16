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

# --- 2. MOTEUR DE RENDU WORD PROFESSIONNEL ---
def create_roll_docx(text_content, cycle_name):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    # En-tête
    title = doc.add_heading(f"FICHE ENSEIGNANT : ACT TYPE 1 - {cycle_name}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    lines = text_content.split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line: continue

        # Titres de sections (Phase 1, 2, etc.)
        if clean_line.startswith(('#', '1.', '2.', '3.', '4.')) or "PHASE" in clean_line.upper():
            doc.add_heading(clean_line.replace('#', '').strip(), level=1)
        
        # Gras
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

    # AJOUT DU TABLEAU DE CONTROVERSE (L'outil central du ROLL)
    doc.add_page_break()
    doc.add_heading("TABLEAU DE CONFRONTATION DES REPRÉSENTATIONS", level=2)
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    cells = table.rows[0].cells
    cells[0].text = "On est d'accord"
    cells[1].text = "On n'est pas d'accord"
    cells[2].text = "On ne sait pas"
    for _ in range(5): table.add_row()

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. INTERFACE ---
st.title("🤖 Expert ROLL : Générateur d'ACT")
st.info("Ce dispositif transforme vos textes en Ateliers de Compréhension (4 phases).")

cycle = st.radio("Cycle concerné :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Support (Word, PDF ou Photo du texte)", type=['docx', 'pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file and st.button("🚀 Générer la fiche complète"):
    with st.spinner('Construction de la fiche selon la méthodologie ROLL...'):
        try:
            # Récupération du contenu du support
            raw_content = ""
            file_data = None
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc_in = Document(uploaded_file)
                raw_content = "\n".join([p.text for p in doc_in.paragraphs])
            elif uploaded_file.type == "application/pdf":
                pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                raw_content = "".join([page.get_text() for page in pdf_doc])
            else: # Image
                file_data = {"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()}

            # LE PROMPT EXPERT INTÉGRÉ
            instruction = f"""Agis en tant qu'expert pédagogique du ROLL. Rédige une fiche enseignant complète pour un ACT de type 1 (narratif) pour le {cycle}.
            
            La fiche doit inclure :
            1. Identification du support (type de texte, genre).
            2. Objectifs de compréhension (Habiletés ROLL) : cibler les personnages et les inférences.
            3. Déroulement en 4 phases :
               - Phase 1 (Lecture individuelle) : Consignes précises.
               - Phase 2 (Émergence) : 3 questions ouvertes + exemples de points de controverse pour le tableau (D'accord / Pas d'accord / Ne sait pas).
               - Phase 3 (Analyse/Vérification) : Modalités de retour au texte avec preuves tangibles (lignes, mots).
               - Phase 4 (Métacognition) : Questions de clôture sur les procédures de lecture.
            4. Prolongements : Activité de mise en réseau ou fiche d'identité.

            Texte support : {raw_content if not file_data else 'Analyse l image jointe.'}
            """

            if file_data:
                response = model.generate_content([instruction, file_data])
            else:
                response = model.generate_content(instruction)
            
            # Affichage et Téléchargement
            st.markdown("---")
            st.markdown(response.text)
            
            docx_output = create_roll_docx(response.text, cycle)
            st.download_button(
                label="📥 Télécharger la Fiche de préparation (Word)",
                data=docx_output,
                file_name=f"ACT_ROLL_{cycle}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")

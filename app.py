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

# --- 2. MOTEUR DE RENDU WORD ---
def create_roll_docx_faithful(text_content, cycle_name):
    doc = Document()
    doc.styles['Normal'].font.name = 'Arial'
    doc.styles['Normal'].font.size = Pt(11)

    title = doc.add_heading(f"FICHE ENSEIGNANT : ACT TYPE 1 - {cycle_name}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    lines = text_content.split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line: continue

        if clean_line.startswith(('#', '1.', '2.', '3.', '4.')) or "PHASE" in clean_line.upper():
            doc.add_heading(clean_line.replace('#', '').strip(), level=1)
        
        elif "|" in clean_line and "---" not in clean_line:
            parts = [p.strip() for p in clean_line.split("|") if p.strip()]
            if len(parts) >= 2:
                table = doc.add_table(rows=1, cols=len(parts))
                table.style = 'Table Grid'
                for i, part in enumerate(parts):
                    table.rows[0].cells[i].text = part
        
        elif '**' in clean_line:
            p = doc.add_paragraph()
            parts = clean_line.split('**')
            for i, part in enumerate(parts):
                run = p.add_run(part)
                if i % 2 != 0: run.bold = True
        
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

if uploaded_file and st.button("🚀 Générer l'analyse spécifique"):
    with st.spinner('Analyse fine des obstacles textuels en cours...'):
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

            # CONSTRUCTION DU PROMPT AVEC FOCUS SUR LES OBSTACLES SPÉCIFIQUES
            instruction = f"Agis en tant qu'expert pédagogique du ROLL. Rédige une fiche enseignant complète pour un ACT de type 1 pour le {cycle}. "
            instruction += "Dans la section 'Objectifs de compréhension', identifie de manière très précise les OBSTACLES SPÉCIFIQUES à ce texte : "
            instruction += "- Lexique complexe ou polysémique présent dans le texte. "
            instruction += "- Ruptures de la chaîne anaphorique (pronoms qui peuvent perdre l'élève). "
            instruction += "- Inférences nécessaires pour comprendre l'implicite de cette histoire précise. "
            instruction += "Respecte les 4 phases habituelles. "
            instruction += "Phase 2 : Propose le tableau pré-rempli avec 3 colonnes (Certitudes, Controverses, Zones d'ombre) basé sur les pièges identifiés plus haut. "
            
            if file_data:
                prompt_final = [instruction + " Analyse l'image jointe pour identifier ces obstacles.", file_data]
            else:
                prompt_final = instruction + f" Texte de référence : {raw_content}"

            response = model.generate_content(prompt_final)
            
            st.markdown("---")
            st.markdown(response.text)
            
            docx_output = create_roll_docx_faithful(response.text, cycle)
            st.download_button(label="📥 Télécharger la Fiche Expert Word", data=docx_output, file_name=f"ACT_ROLL_Expert_{cycle}.docx")
            
        except Exception as e:
            st.error(f"Erreur : {e}")

import streamlit as st
import google.generativeai as genai
import os
import io
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Expert ROLL - Fiche 2 Pages", page_icon="📖")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. MOTEUR DE RENDU WORD COMPACT ---
def create_roll_docx_final(text_content, cycle_name):
    doc = Document()
    
    # Réduction des marges pour tenir sur 2 pages
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(1.2)
        section.bottom_margin = Cm(1.2)
        section.left_margin = Cm(1.5)
        section.right_margin = Cm(1.5)

    doc.styles['Normal'].font.name = 'Arial'
    doc.styles['Normal'].font.size = Pt(10)

    title = doc.add_heading(f"FICHE ACT ROLL : {cycle_name}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    lines = text_content.split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line: continue

        if clean_line.startswith(('#', '1.', '2.', '3.', '4.')) or "PHASE" in clean_line.upper():
            h = doc.add_heading(clean_line.replace('#', '').strip(), level=1)
            h.paragraph_format.space_before = Pt(4)
        
        elif "|" in clean_line and "---" not in clean_line:
            parts = [p.strip() for p in clean_line.split("|") if p.strip()]
            if len(parts) >= 2:
                table = doc.add_table(rows=1, cols=len(parts))
                table.style = 'Table Grid'
                for i, part in enumerate(parts):
                    cell = table.rows[0].cells[i]
                    cell.text = part
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(0)
        
        elif '**' in clean_line:
            p = doc.add_paragraph()
            parts = clean_line.split('**')
            for i, part in enumerate(parts):
                run = p.add_run(part)
                if i % 2 != 0: run.bold = True
            p.paragraph_format.space_after = Pt(1)
        
        elif clean_line.startswith(('-', '*', '•')):
            p = doc.add_paragraph(clean_line.strip('-*• ').strip(), style='List Bullet')
            p.paragraph_format.space_after = Pt(0)
        
        else:
            p = doc.add_paragraph(clean_line)
            p.paragraph_format.space_after = Pt(1)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. INTERFACE ---
st.title("🤖 Expert ROLL")
cycle = st.radio("Cycle :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Texte support", type=['docx', 'pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file and st.button("🚀 Générer la fiche synthétique"):
    with st.spinner('Analyse pédagogique...'):
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

            # PROMPT AVEC LES INTITULÉS DE COLONNES EXACTS
            instruction = f"Agis en tant qu'expert ROLL. Rédige une fiche enseignant SYNTHÉTIQUE (2 pages max) pour un ACT pour le {cycle}. "
            instruction += "Section Objectifs : Analyse les obstacles SPÉCIFIQUES au texte (lexique, anaphores, implicite). "
            instruction += "Phase 2 : Propose impérativement un TABLEAU pré-rempli avec ces trois colonnes exactement : "
            instruction += "1. 'Ce qu'on sait' | 2. 'Ce qu'on ne sait pas' | 3. 'On n'est pas d'accord'. "
            instruction += "Remplis ce tableau avec des exemples de points de controverse et d'incertitude propres au texte."
            
            if file_data:
                prompt_final = [instruction, file_data]
            else:
                prompt_final = instruction + f" Texte : {raw_content}"

            response = model.generate_content(prompt_final)
            
            st.markdown("---")
            st.markdown(response.text)
            
            docx_output = create_roll_docx_final(response.text, cycle)
            st.download_button(label="📥 Télécharger la Fiche (Word)", data=docx_output, file_name=f"ACT_ROLL_Final.docx")
            
        except Exception as e:
            st.error(f"Erreur : {e}")

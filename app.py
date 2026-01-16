import streamlit as st
import google.generativeai as genai
import os
import io
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Expert Pédagogique - ADC", page_icon="📖")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. MOTEUR DE RENDU WORD COMPACT ---
def create_adc_docx_final(text_content, cycle_name):
    doc = Document()
    for section in doc.sections:
        section.top_margin, section.bottom_margin = Cm(1.2), Cm(1.2)
        section.left_margin, section.right_margin = Cm(1.5), Cm(1.5)

    doc.styles['Normal'].font.name, doc.styles['Normal'].font.size = 'Arial', Pt(10)
    title = doc.add_heading(f"FICHE ENSEIGNANT : ATELIER DE COMPRÉHENSION - {cycle_name}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for line in text_content.split('\n'):
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
            for i, part in enumerate(clean_line.split('**')):
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
st.title("🤖 Expert Pédagogique")
st.caption("Générateur d'Ateliers de Compréhension (ADC)")

cycle = st.radio("Niveau :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Texte support (Word, PDF, Scan, Image)", type=['docx', 'pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file and st.button("🚀 Générer la fiche ADC"):
    with st.spinner('Analyse pédagogique et rédaction de la fiche...'):
        try:
            prompt_parts = [f"Agis en tant qu'expert pédagogique. Rédige une fiche enseignant SYNTHÉTIQUE (2 pages max) pour un Atelier de Compréhension (ADC) pour le {cycle}. "]
            prompt_parts[0] += "Section Objectifs : Analyse les obstacles SPÉCIFIQUES au texte (lexique, anaphores, implicite). "
            prompt_parts[0] += "Phase 2 : Tableau pré-rempli avec ces colonnes : 'Ce qu'on sait' | 'Ce qu'on ne sait pas' | 'On n'est pas d'accord'."
            
            if uploaded_file.type == "application/pdf":
                pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                text_content = "".join([page.get_text() for page in pdf_doc])
                if len(text_content.strip()) < 10: # Cas du scan
                    for i in range(len(pdf_doc)):
                        page = pdf_doc.load_page(i)
                        pix = page.get_pixmap()
                        prompt_parts.append({"mime_type": "image/png", "data": pix.tobytes("png")})
                else:
                    prompt_parts.append(f"Texte du support : {text_content}")
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc_in = Document(uploaded_file)
                prompt_parts.append("\n".join([p.text for p in doc_in.paragraphs]))
            else:
                prompt_parts.append({"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()})

            response = model.generate_content(prompt_parts)
            
            st.markdown("---")
            st.markdown(response.text)
            
            docx_output = create_adc_docx_final(response.text, cycle)
            st.download_button(label="📥 Télécharger la Fiche ADC (Word)", data=docx_output, file_name=f"Atelier_Comprehension_{cycle}.docx")
            
        except Exception as e:
            st.error(f"Erreur : {e}")

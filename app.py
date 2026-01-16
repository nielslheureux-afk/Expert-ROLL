import streamlit as st
import google.generativeai as genai
import os
import io
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. FONCTION DE CRÉATION DU WORD (Mise en page Avancée) ---
def create_professional_docx(text_content, cycle_name):
    doc = Document()
    
    # Titre principal stylisé
    title = doc.add_heading(f"FICHE ACT ROLL - {cycle_name}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # On découpe la réponse de l'IA par sections
    sections = text_content.split('\n')
    
    for line in sections:
        line = line.strip().replace('*', '') # On nettoie les symboles markdown
        if not line: continue

        # Détection des titres de sections
        if "ANALYSE" in line.upper() or "QUESTIONS" in line.upper() or "TABLEAU" in line.upper():
            h = doc.add_heading(line, level=1)
        
        # Détection des lignes du tableau (souvent formatées avec "Vrai" ou "Faux" ou des chiffres)
        elif "|" in line or ("Vrai" in line and "/" in line):
            # Si c'est une ligne de tableau, on peut l'ajouter différemment
            p = doc.add_paragraph(line)
            p.paragraph_format.left_indent = Pt(20)
        
        # Listes à puces
        elif line.startswith('-') or line.startswith('•'):
            doc.add_paragraph(line, style='List Bullet')
            
        else:
            doc.add_paragraph(line)

    # Ajout d'un vrai tableau à la fin pour le débat (si présent dans le texte)
    # Note : On peut forcer une structure de tableau vide pour que l'enseignant le remplisse
    doc.add_page_break()
    doc.add_heading("TABLEAU DE DÉBAT (Espace Élèves)", level=2)
    table = doc.add_table(rows=5, cols=2)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Affirmations'
    hdr_cells[1].text = 'Accord / Désaccord'

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. INTERFACE ---
st.title("🤖 Expert ROLL")
cycle = st.radio("Niveau :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Document (Word, PDF, JPG, PNG)", type=['docx', 'pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file and st.button("🚀 Lancer l'analyse haute qualité"):
    with st.spinner('Analyse ROLL en cours...'):
        try:
            content_to_send = []
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc_in = Document(uploaded_file)
                text_content = "\n".join([p.text for p in doc_in.paragraphs])
                content_to_send.append(text_content)
            elif uploaded_file.type == "application/pdf":
                pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                content_to_send.append("".join([page.get_text() for page in pdf_doc]))
            elif uploaded_file.type in ["image/jpeg", "image/png"]:
                content_to_send.append({"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()})

            prompt = f"Expert ROLL. Crée un ACT pour le {cycle}. Structure : 1. Analyse obstacles, 2. Questions émergence, 3. Tableau débat (Affirmations Vrai/Faux)."

            if isinstance(content_to_send[0], dict):
                response = model.generate_content([prompt, content_to_send[0]])
            else:
                response = model.generate_content(prompt + "\n" + content_to_send[0])
            
            # Affichage écran (On utilise code pour éviter le bug de récursion)
            st.success("Analyse terminée !")
            with st.expander("Voir l'analyse détaillée"):
                st.write(response.text)
            
            # Génération du Word stylisé
            docx_output = create_professional_docx(response.text, cycle)
            
            st.download_button(
                label="📥 TÉLÉCHARGER LA FICHE WORD (Format Imprimable)",
                data=docx_output,
                file_name=f"FICHE_ACT_{cycle}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        except Exception as e:
            st.error(f"Erreur : {e}")

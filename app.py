import streamlit as st
import google.generativeai as genai
import os
import io
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. FONCTION DE CRÉATION DU WORD FIDÈLE ---
def create_faithful_docx(text_content, cycle_name):
    doc = Document()
    
    # Style par défaut (Arial pour la lisibilité)
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    # Titre Principal
    t = doc.add_heading(f"FICHE ACT ROLL - {cycle_name}", 0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER

    lines = text_content.split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        # Gestion des Titres (ex: ### Titre ou Titre souligné)
        if clean_line.startswith('#'):
            level = clean_line.count('#')
            doc.add_heading(clean_line.replace('#', '').strip(), level=min(level, 3))
        
        # Gestion des Listes à puces
        elif clean_line.startswith(('-', '*', '•')):
            p = doc.add_paragraph(clean_line.strip('-*• ').strip(), style='List Bullet')
        
        # Gestion du Gras (Texte entre **)
        elif '**' in clean_line:
            p = doc.add_paragraph()
            parts = clean_line.split('**')
            for i, part in enumerate(parts):
                run = p.add_run(part)
                if i % 2 != 0:  # Les parties impaires sont entre les **
                    run.bold = True
        
        # Paragraphe normal
        else:
            doc.add_paragraph(clean_line)

    # Ajout automatique d'un vrai tableau de débat structuré
    doc.add_page_break()
    doc.add_heading("TABLEAU DE DÉBAT (EVALUATION)", level=1)
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Affirmation'
    hdr_cells[1].text = 'Vrai'
    hdr_cells[2].text = 'Faux'
    
    # On ajoute 4 lignes vides prêtes à l'emploi
    for _ in range(4):
        table.add_row()

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. INTERFACE ---
st.title("🤖 Expert ROLL")
cycle = st.radio("Niveau scolaire :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Document (Word, PDF, Image)", type=['docx', 'pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file and st.button("🚀 Lancer l'analyse"):
    with st.spinner('Analyse ROLL en cours...'):
        try:
            # Extraction du contenu
            content_to_send = []
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc_in = Document(uploaded_file)
                content_to_send.append("\n".join([p.text for p in doc_in.paragraphs]))
            elif uploaded_file.type == "application/pdf":
                pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                content_to_send.append("".join([page.get_text() for page in pdf_doc]))
            elif uploaded_file.type in ["image/jpeg", "image/png"]:
                content_to_send.append({"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()})

            # Prompt renforcé pour la mise en page
            prompt = f"""Tu es un expert ROLL. Conçois un ACT pour le {cycle}.
            Utilise impérativement ce format :
            # ANALYSE DES OBSTACLES
            (Ton analyse ici)
            # QUESTIONS D'ÉMERGENCE
            - Question 1...
            - Question 2...
            # PROPOSITIONS POUR LE DÉBAT
            **Affirmation 1** : (texte)
            **Affirmation 2** : (texte)
            """

            if isinstance(content_to_send[0], dict):
                response = model.generate_content([prompt, content_to_send[0]])
            else:
                response = model.generate_content(prompt + "\n" + content_to_send[0])
            
            # AFFICHAGE ÉCRAN
            st.markdown("---")
            st.markdown(response.text) # Ici le rendu est beau
            
            # GÉNÉRATION WORD FIDÈLE
            docx_output = create_faithful_docx(response.text, cycle)
            
            st.download_button(
                label="📥 TÉLÉCHARGER LA FICHE WORD (Format Imprimable)",
                data=docx_output,
                file_name=f"ACT_ROLL_{cycle}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        except Exception as e:
            st.error(f"Erreur : {e}")

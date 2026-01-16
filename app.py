import streamlit as st
import google.generativeai as genai
import os
import io
import fitz  # PyMuPDF
from docx import Document

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. FONCTION WORD SÉCURISÉE ---
def create_docx(text, cycle_name):
    doc = Document()
    doc.add_heading(f"Fiche ACT ROLL - {cycle_name}", 0)
    # On sépare le texte proprement pour éviter les problèmes de caractères
    for line in text.split('\n'):
        clean = line.strip()
        if clean:
            # On retire les symboles Markdown qui font planter l'affichage
            clean = clean.replace('**', '').replace('###', '').replace('#', '')
            doc.add_paragraph(clean)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. INTERFACE ---
st.title("Expert ROLL")
cycle = st.radio("Niveau :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Fichier Word, PDF ou Image", type=['docx', 'pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file and st.button("Lancer l'analyse"):
    with st.spinner('Analyse ROLL en cours...'):
        try:
            content_to_send = []
            
            # Gestion des fichiers
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc_in = Document(uploaded_file)
                text_content = "\n".join([p.text for p in doc_in.paragraphs])
                content_to_send.append(f"Texte :\n{text_content}")

            elif uploaded_file.type == "application/pdf":
                pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                text_content = "".join([page.get_text() for page in pdf_doc])
                content_to_send.append(f"Texte PDF :\n{text_content}")

            elif uploaded_file.type in ["image/jpeg", "image/png"]:
                image_data = uploaded_file.getvalue()
                content_to_send.append({"mime_type": uploaded_file.type, "data": image_data})

            prompt = f"Expert ROLL. Crée un ACT pour le {cycle}. Analyse obstacles, 3 questions, tableau débat Vrai/Faux."

            # Envoi à Gemini
            if isinstance(content_to_send[0], dict):
                response = model.generate_content([prompt, content_to_send[0]])
            else:
                response = model.generate_content(prompt + "\n" + content_to_send[0])
            
            # --- AFFICHAGE SÉCURISÉ POUR ÉVITER LA RÉCURSION ---
            st.success("Analyse terminée !")
            
            # On utilise un conteneur de texte brut si le markdown plante
            st.text_area("Aperçu du texte généré (copie possible) :", value=response.text, height=300)
            
            # Génération immédiate du Word
            docx_output = create_docx(response.text, cycle)
            
            st.download_button(
                label="📥 Télécharger la fiche Word (Mise en page propre)",
                data=docx_output,
                file_name=f"ACT_ROLL_{cycle}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        except Exception as e:
            st.error(f"Erreur technique : {e}")

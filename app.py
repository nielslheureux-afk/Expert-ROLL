import streamlit as st
import google.generativeai as genai
import os
from docx import Document

# --- CONFIGURATION ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")
st.title("🤖 Expert ROLL : Générateur d'ACT (v3)")

api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # On utilise le modèle correspondant à votre interface
    model = genai.GenerativeModel('gemini-3-flash')
else:
    st.info("👋 Veuillez ajouter votre GEMINI_API_KEY dans les Secrets.")
    st.stop()

# --- INTERFACE ---
cycle = st.radio("Cycle :", ["Cycle 2", "Cycle 3"])
file = st.file_uploader("Document", type=['docx', 'jpg', 'png', 'pdf'])

if file and st.button("🚀 Générer"):
    with st.spinner('Analyse avec Gemini 3...'):
        try:
            prompt = f"Expert ROLL. Conçois un ACT pour le {cycle}. Analyse obstacles, 3 questions, tableau débat."
            
            if file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(file)
                text = "\n".join([p.text for p in doc.paragraphs])
                response = model.generate_content([prompt, text])
            else:
                data = file.read()
                response = model.generate_content([prompt, {"mime_type": file.type, "data": data}])

            st.markdown(response.text)
            st.download_button("Télécharger", response.text, file_name="ACT_ROLL.txt")
            
        except Exception as e:
            # Si gemini-3-flash est trop récent pour votre bibliothèque Python
            st.error(f"Erreur : {e}")
            st.info("Essayez de remplacer 'gemini-3-flash' par 'gemini-1.5-flash' ou 'gemini-1.5-pro' dans le code si l'erreur persiste.")

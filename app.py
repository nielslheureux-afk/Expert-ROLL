import streamlit as st
import google.generativeai as genai
import os
from docx import Document

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

# --- INTERFACE ---
st.title("🤖 Expert ROLL : Générateur d'ACT")
cycle_choisi = st.radio("Niveau :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Document", type=['pdf', 'docx', 'jpg', 'png'])

# --- CONFIGURATION IA (CORRECTIF RADICAL) ---
api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    # On force le transport 'rest' ET on définit manuellement le modèle
    genai.configure(api_key=api_key, transport='rest')
    
    # On essaie d'abord le 1.5-flash, sinon on bascule sur le 1.5-pro
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('models/gemini-1.5-pro')
else:
    st.info("Configuration : Ajoutez la clé dans les Secrets.")
    st.stop()

# --- GÉNÉRATION ---
if uploaded_file and st.button("🚀 Générer la fiche"):
    with st.spinner('Analyse en cours...'):
        try:
            prompt = f"Expert ROLL. Conçois un ACT pour le {cycle_choisi}. Analyse obstacles, questions, tableau débat."
            
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(uploaded_file)
                text = "\n".join([p.text for p in doc.paragraphs])
                response = model.generate_content(prompt + "\nTexte : " + text)
            else:
                img_data = uploaded_file.read()
                response = model.generate_content([prompt, {"mime_type": uploaded_file.type, "data": img_data}])

            st.markdown(response.text)
        except Exception as e:
            st.error(f"Erreur : {e}")

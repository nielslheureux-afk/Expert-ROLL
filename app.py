import streamlit as st
import google.generativeai as genai
import os

# 1. Configuration de l'API
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

# On force le transport 'rest' pour éviter l'erreur v1beta
genai.configure(api_key=api_key, transport='rest')

# 2. Configuration du modèle avec le chemin complet
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

# 3. Interface simple pour tester
st.title("Test Expert ROLL")
uploaded_file = st.file_uploader("Charger un document", type=['pdf', 'docx', 'png', 'jpg'])

if uploaded_file and st.button("Lancer l'analyse"):
    with st.spinner("Analyse en cours..."):
        try:
            # Test d'envoi simple
            response = model.generate_content("Dis bonjour et analyse brièvement ce document.")
            st.write(response.text)
        except Exception as e:
            st.error(f"Détails de l'erreur : {e}")

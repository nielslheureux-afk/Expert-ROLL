import streamlit as st
import google.generativeai as genai
import os
from docx import Document

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

# --- 2. INTERFACE UTILISATEUR ---
st.title("🤖 Expert ROLL : Générateur d'ACT")
st.markdown("Outil d'aide à la préparation des Ateliers de Compréhension de Texte.")

cycle_choisi = st.radio(
    "Niveau scolaire :",
    ["Cycle 2 (CP, CE1, CE2)", "Cycle 3 (CM1, CM2, 6ème)"],
    index=0
)

uploaded_file = st.file_uploader("Document (Image, PDF ou Word)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

# --- 3. CONFIGURATION DE LA CLÉ API ---
# Récupération depuis les Secrets de Streamlit
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.info("👋 **Configuration requise** : Veuillez ajouter votre clé API dans les Secrets de Streamlit.")
    st.stop()

# --- 4. INITIALISATION DE L'IA (SYNTAXE ANTI-ERREUR 404) ---
try:
    # On configure l'API
    genai.configure(api_key=api_key)
    
    # On appelle le modèle avec son nom complet pour forcer la reconnaissance
    model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
except Exception as e:
    st.error(f"Erreur d'initialisation : {e}")
    st.stop()

# --- 5. LOGIQUE DE GÉNÉRATION ---
if uploaded_file is not None:
    if st.button("🚀 Générer la fiche pédagogique"):
        with st.spinner('Analyse pédagogique en cours...'):
            try:
                # Définition du prompt
                prompt = f"""Agis en tant qu'expert pédagogique du ROLL. 
                Conçois un Atelier de Compréhension de Texte (ACT) pour le {cycle_choisi}.
                Structure : 1. Analyse des obstacles, 2. Questions d'émergence, 3. Tableau débat, 4. Métacognition.
                Ne recopie pas le texte original."""

                # Traitement du fichier Word ou Image/PDF
                if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(uploaded_file)
                    full_text = "\n".join([p.text for p in doc.paragraphs])
                    # Envoi en format texte pur
                    response = model.generate_content([prompt, full_text])
                else:
                    # Envoi en format multimodal (Image/PDF)
                    file_data = uploaded_file.read()
                    content_parts = [
                        prompt,
                        {"mime_type": uploaded_file.type, "data": file_data}

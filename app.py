import streamlit as st
import google.generativeai as genai
from google.api_core import client_options
from docx import Document
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖", layout="centered")

# --- 2. INTERFACE UTILISATEUR (S'affiche toujours) ---
st.title("🤖 Expert ROLL : Générateur d'ACT")
st.markdown("Créez vos Ateliers de Compréhension de Texte en quelques secondes.")

cycle_choisi = st.radio(
    "Niveau scolaire :",
    ["Cycle 2 (CP, CE1, CE2)", "Cycle 3 (CM1, CM2, 6ème)"],
    index=0
)

uploaded_file = st.file_uploader("Chargez votre texte (Image, PDF ou Word)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

# --- 3. GESTION DE LA CLÉ ET DE L'IA ---
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.info("👋 **Bienvenue !** Pour activer l'IA, ajoutez votre clé API dans les **Secrets** de Streamlit.")
    with st.expander("Comment faire ?"):
        st.write("1. Allez dans Settings > Secrets de votre app Streamlit.")
        st.write('2. Collez : `GEMINI_API_KEY = "votre_cle_ici"`')
    st.stop()

# --- 4. CONFIGURATION SÉCURISÉE (ANTI-ERREUR 404) ---
try:
    # On force l'utilisation de la version stable 'v1'
    options = client_options.ClientOptions(api_version='v1')
    genai.configure(api_key=api_key, transport='rest', client_options=options)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erreur de configuration : {e}")
    st.stop()

# --- 5. LOGIQUE DE GÉNÉRATION ---
if uploaded_file is not None:
    if st.button("🚀 Générer la fiche pédagogique"):
        with st.spinner('L\'IA analyse votre document...'):
            try:
                # Préparation du prompt pédagogique
                prompt = f"""
                Agis en tant qu'expert pédagogique du ROLL. 
                Conçois un Atelier de Compréhension de Texte (ACT) pour le {cycle_choisi}.
                
                Structure requise :
                1. ANALYSE DU SUPPORT (Obstacles, lexique, implicite).
                2. PHASE 1 : Consigne de lecture.
                3. PHASE 2 : 3 questions d'émergence + Tableau 'D'accord/Pas d'accord'.
                4. PHASE 3 : Guidage pour la confrontation au texte.
                5. PHASE 4 : Métacognition (Stratégie travaillée).
                
                IMPORTANT : Ne recopie pas le texte original.
                """
                
                # Extraction du contenu selon le fichier
                if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(uploaded_file)
                    text_content = "\n".join([p.text for p in doc.paragraphs])
                    content = [prompt, f"Texte à analyser : \n{text_content}"]
                else:
                    file_data = uploaded_file.read()
                    content = [prompt, {"mime_type": uploaded_file.type, "data": file_data}]

                # Génération par l'IA
                response = model.generate_content(content)

                if response.text:
                    st.success("✅ Fiche générée !")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                    # Bouton de téléchargement
                    st.download_button(
                        label="

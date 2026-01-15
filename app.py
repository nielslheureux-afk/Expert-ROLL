import streamlit as st
import google.generativeai as genai
import os
from docx import Document

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

# --- 2. GESTION DE LA CLÉ API ---
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.title("🤖 Expert ROLL")
    st.info("👋 Bienvenue ! Veuillez configurer votre clé API dans les Secrets de Streamlit pour activer l'IA.")
    st.stop()

# --- 3. DÉTECTION AUTOMATIQUE DU MODÈLE (Anti-Erreur 404) ---
genai.configure(api_key=api_key)

@st.cache_resource
def load_best_model():
    try:
        # On interroge Google pour voir les modèles actifs sur votre compte
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # On cherche le modèle le plus moderne (Gemini 3 ou 2)
        for name in ["models/gemini-3-flash", "models/gemini-2.0-flash", "models/gemini-1.5-flash"]:
            if name in available_models:
                return genai.GenerativeModel(name), name
        
        # Si rien n'est trouvé, on prend le premier disponible
        return genai.GenerativeModel(available_models[0]), available_models[0]
    except Exception as e:
        st.error(f"Erreur lors de la détection du modèle : {e}")
        return None, None

model, model_name = load_best_model()

# --- 4. INTERFACE UTILISATEUR ---
st.title(f"🤖 Expert ROLL")
if model_name:
    st.caption(f"Connecté via : {model_name} (Quota : 1500 requêtes/jour)")

cycle_choisi = st.radio("Niveau scolaire :", ["Cycle 2 (CP-CE)", "Cycle 3 (CM-6ème)"])
uploaded_file = st.file_uploader("Document (Image, PDF ou Word)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

# --- 5. GÉNÉRATION ---
if uploaded_file is not None and model:
    if st.button("🚀 Générer la fiche pédagogique"):
        with st.spinner('Analyse pédagogique en cours...'):
            try:
                prompt = f"Expert ROLL. Conçois un ACT pour le {cycle_choisi}. Analyse les obstacles, propose 3 questions et un tableau débat. Ne recopie pas le texte."
                
                if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(uploaded_file)
                    text = "\n".join([p.text for p in doc.paragraphs])
                    response = model.generate_content([prompt, text])
                else:
                    data = uploaded_file.read()
                    response = model.generate_content([prompt, {"mime_type": uploaded_file.type, "data": data}])

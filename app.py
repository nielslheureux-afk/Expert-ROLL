import streamlit as st
import google.generativeai as genai
import os
from docx import Document

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

# --- 2. GESTION DE LA CLÉ ---
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.title("🤖 Expert ROLL")
    st.info("Ajoutez votre clé API dans les Secrets pour commencer.")
    st.stop()

# --- 3. CONFIGURATION IA ---
genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        # On cherche dynamiquement le meilleur modèle disponible (Gemini 3 ou 1.5)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for target in ["models/gemini-3-flash", "models/gemini-1.5-flash"]:
            if target in models:
                return genai.GenerativeModel(target), target
        return genai.GenerativeModel(models[0]), models[0]
    except:
        return genai.GenerativeModel('gemini-1.5-flash'), "gemini-1.5-flash"

model, model_name = load_model()

# --- 4. INTERFACE ---
st.title("🤖 Expert ROLL")
if model_name:
    st.caption(f"Connecté via : {model_name}")

cycle = st.radio("Niveau :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Fichier (Image, PDF ou Word)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

# --- 5. LOGIQUE DE GÉNÉRATION ---
if uploaded_file and st.button("🚀 Générer la fiche"):
    with st.spinner('Analyse...'):
        try:
            prompt = f"Expert ROLL. Conçois un ACT pour le {cycle}. Analyse obstacles, 3 questions, tableau débat."
            
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(uploaded_file)
                text = "\n".join([p.text for p in doc.paragraphs])
                response = model.generate_content([prompt, text])
            else:
                data = uploaded_file.read()
                response = model.generate_content([
                    prompt, 
                    {"mime_type": uploaded_file.type, "data": data}
                ])

            if response.text:
                st.success("Fiche générée !")
                st.markdown(response.text)
                st.download_button("📥 Télécharger", response.text, file_name="ACT_ROLL.txt")
        
        except Exception as e:
            st.error(f"Erreur lors de la génération : {e}")
            st.info("Si vous voyez une erreur 404, supprimez et recréez l'app sur Streamlit.")

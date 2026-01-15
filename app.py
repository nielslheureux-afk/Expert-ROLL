import streamlit as st
import google.generativeai as genai
import os

# 1. Configuration initiale
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# 2. DÉTECTION AUTOMATIQUE DU MODÈLE (La solution)
@st.cache_resource
def get_model_name():
    try:
        # On liste les modèles pour voir ce que votre clé autorise vraiment
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # On cherche en priorité un modèle "Flash" pour la vitesse
                if 'flash' in m.name:
                    return m.name
        return 'models/gemini-1.5-pro' # Repli par défaut
    except Exception:
        return 'models/gemini-1.5-flash'

target_model = get_model_name()
model = genai.GenerativeModel(target_model)

st.success(f"Connecté avec succès au modèle : {target_model}")

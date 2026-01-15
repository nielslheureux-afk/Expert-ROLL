import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from docx import Document
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

# --- 2. CONFIGURATION DE L'API ---
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Clé API manquante dans les Secrets de Streamlit.")
    st.stop()

# FORCE LE PASSAGE EN V1 (STABLE) VIA LE TRANSPORT 'REST'
genai.configure(api_key=api_key, transport='rest')

# --- 3. CONFIGURATION DU MODÈLE ---
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# Utilisation du modèle 1.5 Flash
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    safety_settings=safety_settings
)

# --- 4. INTERFACE ---
st.title("🤖 Expert ROLL : Générateur d'ACT")

cycle_choisi = st.radio(
    "Niveau scolaire :",
    ["Cycle 2 (CP, CE1, CE2)", "Cycle 3 (CM1, CM2, 6ème)"]
)

uploaded_file = st.file_uploader("Document (Image, PDF ou Word)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

# --- 5. LOGIQUE ---
def obtenir_prompt(cycle):
    base_prompt = "Agis en tant qu'expert pédagogique du ROLL. Conçois un Atelier de Compréhension de Texte (ACT) avec analyse du support, phase d'émergence (3 questions), tableau débat et métacognition. Ne recopie pas le texte original."
    if "Cycle 2" in cycle:
        return base_prompt + " Focus : chronologie et explicite."
    return base_prompt + " Focus : implicite et intentions des personnages."

# --- 6. GÉNÉRATION ---
if uploaded_file is not None:
    if st.button("Générer la fiche"):
        with st.spinner('Analyse en cours...'):
            try:
                prompt = obtenir_prompt(cycle_choisi)
                
                if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(uploaded_file)
                    text = "\n".join([p.text for p in doc.paragraphs])
                    content = [prompt, f"Texte : {text}"]
                else:
                    file_data = uploaded_file.read()
                    content = [prompt, {"mime_type": uploaded_file.type, "data": file_data}]

                # Appel à l'IA
                response = model.generate_content(content)
                
                if response.text:
                    st.success("Fiche générée !")
                    st.markdown(response.text)
                    st.download_button("Télécharger", response.text, file_name="fiche_roll.txt")
            except Exception as e:
                st.error(f"Erreur : {e}")

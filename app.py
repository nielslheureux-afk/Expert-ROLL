import streamlit as st
import google.generativeai as genai
import os
import io
from docx import Document

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# --- 2. DÉTECTION DYNAMIQUE (Pour éviter l'erreur 404) ---
@st.cache_resource
def find_working_model():
    try:
        # On liste les modèles pour trouver le nom exact utilisé en 2026
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # On cherche un modèle Flash (pour le quota gratuit)
                if 'flash' in m.name.lower():
                    return m.name
        return "models/gemini-pro" # Secours
    except:
        return "gemini-1.5-flash" # Dernier recours

target_model_name = find_working_model()
model = genai.GenerativeModel(target_model_name)

# --- 3. FONCTION WORD ---
def create_docx(text, cycle_name):
    doc = Document()
    doc.add_heading(f"Fiche ACT ROLL - {cycle_name}", 0)
    for line in text.split('\n'):
        clean = line.replace('*', '').replace('#', '').strip()
        if clean:
            doc.add_paragraph(clean)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. INTERFACE ---
st.title("Expert ROLL")
st.caption(f"Connecté via : {target_model_name}")

cycle = st.radio("Niveau :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Fichier Word (.docx)", type=['docx'])

if uploaded_file and st.button("Lancer l'analyse"):
    with st.spinner('Analyse ROLL en cours...'):
        try:
            doc_in = Document(uploaded_file)
            content = "\n".join([p.text for p in doc_in.paragraphs])

            prompt = f"""Expert ROLL. Crée un ACT pour le {cycle}. 
            1. Analyse précise des obstacles (lexique, implicite). 
            2. 3 questions d'émergence. 
            3. Tableau débat Vrai/Faux.
            Texte : {content}"""

            response = model.generate_content(prompt)
            
            st.markdown("---")
            st.markdown(response.text)
            
            docx_output = create_docx(response.text, cycle)
            st.download_button("Télécharger en Word", data=docx_output, file_name="ACT_ROLL.docx")
            
        except Exception as e:
            st.error(f"Détails de l'erreur : {e}")

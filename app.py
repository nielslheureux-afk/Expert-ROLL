import streamlit as st
import google.generativeai as genai
from docx import Document
import os

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

# --- INTERFACE ---
st.title("🤖 Expert ROLL : Générateur d'ACT")

cycle_choisi = st.radio(
    "Niveau scolaire :",
    ["Cycle 2 (CP, CE1, CE2)", "Cycle 3 (CM1, CM2, 6ème)"],
    index=0
)

uploaded_file = st.file_uploader("Document (Image, PDF ou Word)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

# --- GESTION DE LA CLÉ ---
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.info("👋 Configuration : Ajoutez votre clé API dans les Secrets.")
    st.stop()

# --- CONFIGURATION IA SIMPLIFIÉE ---
# On enlève tout ce qui est complexe pour éviter les erreurs de version
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- GÉNÉRATION ---
if uploaded_file is not None:
    if st.button("🚀 Générer la fiche"):
        with st.spinner('Analyse en cours...'):
            try:
                prompt = f"Agis en tant qu'expert ROLL. Conçois un ACT pour le {cycle_choisi}. Analyse les obstacles, propose 3 questions et un tableau débat. Ne recopie pas le texte."
                
                if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(uploaded_file)
                    text_content = "\n".join([p.text for p in doc.paragraphs])
                    content = [prompt, f"Texte : \n{text_content}"]
                else:
                    file_data = uploaded_file.read()
                    content = [prompt, {"mime_type": uploaded_file.type, "data": file_data}]

                response = model.generate_content(content)

                if response.text:
                    st.success("✅ Fiche générée !")
                    st.markdown("---")
                    st.markdown(response.text)
                    st.download_button("Télécharger", response.text, file_name="ACT_ROLL.txt")

            except Exception as e:
                st.error(f"Erreur : {e}")

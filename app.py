import streamlit as st
import google.generativeai as genai
import os
from docx import Document

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

# 2. INTERFACE UTILISATEUR
st.title("🤖 Expert ROLL : Générateur d'ACT")

cycle_choisi = st.radio(
    "Niveau scolaire :",
    ["Cycle 2 (CP, CE1, CE2)", "Cycle 3 (CM1, CM2, 6ème)"],
    index=0
)

uploaded_file = st.file_uploader("Document (Image, PDF ou Word)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

# 3. GESTION DE LA CLÉ API
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.info("👋 Configuration : Ajoutez votre clé API dans les Secrets de Streamlit.")
    st.stop()

# 4. CONFIGURATION DE L'IA
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

# 5. GÉNÉRATION
if uploaded_file is not None:
    if st.button("🚀 Générer la fiche pédagogique"):
        with st.spinner('Analyse pédagogique en cours...'):
            try:
                # Prompt simplifié pour éviter les erreurs de texte
                prompt = f"Agis en tant qu'expert ROLL. Conçois un ACT pour le {cycle_choisi}. Analyse les obstacles, propose 3 questions et un tableau débat. Ne recopie pas le texte original."

                # Traitement selon le type de fichier
                if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(uploaded_file)
                    text_content = "\n".join([p.text for p in doc.paragraphs])
                    response = model.generate_content(prompt + "\n\nTexte :\n" + text_content)
                else:
                    # Pour PDF et Images
                    file_bytes = uploaded_file.read()
                    response = model.generate_content([
                        prompt,
                        {"mime_type": uploaded_file.type, "data": file_bytes}
                    ])

                # Affichage du résultat
                if response.text:
                    st.success("✅ Fiche générée !")
                    st.markdown("---")
                    st.markdown(response.text)
                    st.download_button("📥 Télécharger", response.text, file_name="ACT_ROLL.txt")

            except Exception as e:
                st.error(f"Erreur : {e}")

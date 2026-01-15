import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from docx import Document
import os

# 1. CONFIGURATION DE L'IA (SÉCURISÉE ET FORCÉE EN V1)
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("ERREUR : La clé API est manquante dans les Secrets.")
    st.stop()

# Le paramètre transport='rest' force l'utilisation de l'API stable (v1)
genai.configure(api_key=api_key, transport='rest')

# Configuration du modèle 1.5 Flash (le plus généreux en quota)
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    safety_settings=safety_settings
)

# 2. INTERFACE STREAMLIT
st.set_page_config(page_title="Expert ROLL", page_icon="📖")
st.title("🤖 Expert ROLL : Générateur d'ACT")

cycle_choisi = st.radio(
    "Pour quel niveau souhaitez-vous préparer cet ACT ?",
    ["Cycle 2 (CP, CE1, CE2)", "Cycle 3 (CM1, CM2, 6ème)"],
    index=0
)

uploaded_file = st.file_uploader("Chargez votre texte (Image, PDF ou Word)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

# 3. LOGIQUE PEDAGOGIQUE
def obtenir_prompt(cycle):
    base_prompt = """
    Agis en tant qu'expert pédagogique du ROLL. 
    Conçois un Atelier de Compréhension de Texte (ACT) à partir du document fourni.
    Structure :
    1. ANALYSE DU SUPPORT (Obstacles, inférences).
    2. PHASE 1 : Lecture individuelle.
    3. PHASE 2 : Émergence des représentations (3 questions + tableau 'D'accord/Pas d'accord').
    4. PHASE 3 : Confrontation au texte.
    5. PHASE 4 : Métacognition.
    IMPORTANT : Ne recopie pas le texte original (droits d'auteur).
    """
    if "Cycle 2" in cycle:
        return base_prompt + " CONSIGNE CYCLE 2 : Focalise sur la chronologie et les sentiments explicites."
    else:
        return base_prompt + " CONSIGNE CYCLE 3 : Focalise sur l'implicite complexe et les non-dits."

# 4. TRAITEMENT
if uploaded_file is not None:
    with st.spinner('L\'IA analyse votre document...'):
        try:
            prompt_final = obtenir_prompt(cycle_choisi)
            
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(uploaded_file)
                text = "\n".join([p.text for p in doc.paragraphs])
                content = [prompt_final, f"Texte : \n{text}"]
            else:
                file_data = uploaded_file.read()
                content = [prompt_final, {"mime_type": uploaded_file.type, "data": file_data}]

            response = model.generate_content(content)

            if response.text:
                st.success(f"Fiche {cycle_choisi} générée !")
                st.markdown(response.text)
                st.download_button("Télécharger la fiche", response.text, file_name="fiche_ROLL.txt")
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")

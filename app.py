import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from docx import Document

# 1. CONFIGURATION DE L'IA
# Remplacez bien 'VOTRE_CLE_API' par votre véritable clé
genai.configure(api_key="AIzaSyAiRPVBddpl0da12mhDTejPbj9_HyGw8Ss")

# Réglages de sécurité pour éviter les blocages sur les albums jeunesse
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    safety_settings=safety_settings
)

# 2. INTERFACE STREAMLIT
st.set_page_config(page_title="Expert ROLL", page_icon="📖", layout="wide")
st.title("🤖 Expert ROLL : Générateur d'ACT")

# Nouveau : Sélection du niveau pour adapter la difficulté
cycle_choisi = st.radio(
    "Pour quel niveau souhaitez-vous préparer cet ACT ?",
    ["Cycle 2 (CP, CE1, CE2)", "Cycle 3 (CM1, CM2, 6ème)"],
    index=0
)

uploaded_file = st.file_uploader("Chargez votre texte (Image, PDF ou Word)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

# 3. LOGIQUE PEDAGOGIQUE DYNAMIQUE
def obtenir_prompt(cycle):
    base_prompt = """
    Agis en tant qu'expert pédagogique du ROLL. 
    Ta mission est de concevoir un Atelier de Compréhension de Texte (ACT) à partir du document fourni.
    Respecte impérativement cette structure :
    1. ANALYSE DU SUPPORT : Obstacles (inférences), intentions des personnages.
    2. PHASE 1 : Lecture individuelle.
    3. PHASE 2 : Émergence des représentations. Propose 3 questions ouvertes adaptées au niveau choisi.
       Génère un tableau 'D'accord / Pas d'accord / On ne sait pas' pour le débat.
    4. PHASE 3 : Confrontation au texte (arbitrage).
    5. PHASE 4 : Métacognition (stratégies de lecture).
    
    IMPORTANT : Ne recopie pas le texte original par respect des droits d'auteur, produis uniquement l'analyse.
    """
    
    if "Cycle 2" in cycle:
        return base_prompt + """
        CONSIGNE SPECIFIQUE CYCLE 2 : Focalise sur la compréhension littérale, la chronologie et les sentiments explicites. 
        Utilise un vocabulaire simple pour les questions. Aide les élèves à identifier 'Qui fait quoi'."""
    else:
        return base_prompt + """
        CONSIGNE SPECIFIQUE CYCLE 3 : Focalise sur l'implicite complexe, les non-dits et l'évolution psychologique des personnages. 
        Pousse l'analyse sur les 'blancs' du texte et les interprétations divergentes."""

# 4. TRAITEMENT DU FICHIER
if uploaded_file is not None:
    with st.spinner(f'Analyse en cours pour le {cycle_choisi}...'):
        try:
            prompt_final = obtenir_prompt(cycle_choisi)
            
            # Gestion du format Word
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(uploaded_file)
                text = "\n".join([p.text for p in doc.paragraphs])
                content = [prompt_final, f"Texte à analyser : \n{text}"]
            # Gestion PDF et Images
            else:
                file_data = uploaded_file.read()
                content = [prompt_final, {"mime_type": uploaded_file.type, "data": file_data}]

            # Appel à l'IA
            response = model.generate_content(content)

            # Affichage sécurisé des résultats
            if response.candidates and len(response.candidates[0].content.parts) > 0:
                resultat = response.candidates[0].content.parts[0].text
                st.success(f"Fiche {cycle_choisi} générée !")
                st.markdown(resultat)
                st.download_button("Télécharger la fiche", resultat, file_name=f"ACT_ROLL_{cycle_choisi}.txt")
            else:
                st.error("L'IA n'a pas pu produire de texte. Vérifiez la lisibilité du document.")

        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")
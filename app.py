import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from docx import Document
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖", layout="wide")

# --- 2. GESTION SÉCURISÉE DE LA CLÉ API ---
# On récupère la clé depuis les "Secrets" de Streamlit
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ La clé API est manquante. Veuillez la configurer dans les Settings > Secrets de Streamlit.")
    st.stop()

# Configuration forcée en mode 'rest' pour éviter l'erreur 404/v1beta
genai.configure(api_key=api_key, transport='rest')

# --- 3. CONFIGURATION DU MODÈLE ---
# On utilise Gemini 1.5 Flash (le plus performant pour les quotas gratuits)
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

# --- 4. INTERFACE UTILISATEUR ---
st.title("🤖 Expert ROLL : Générateur d'ACT")
st.markdown("Cet outil génère une fiche d'Atelier de Compréhension de Texte (ACT) basée sur la pédagogie du ROLL.")

col1, col2 = st.columns([1, 1])

with col1:
    cycle_choisi = st.radio(
        "Niveau scolaire :",
        ["Cycle 2 (CP, CE1, CE2)", "Cycle 3 (CM1, CM2, 6ème)"],
        index=0
    )

with col2:
    uploaded_file = st.file_uploader("Document (Image, PDF ou Word)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

# --- 5. LOGIQUE PÉDAGOGIQUE ---
def obtenir_prompt(cycle):
    base_prompt = """
    Agis en tant qu'expert pédagogique du ROLL (Réseau des Observatoires Locaux de la Lecture). 
    Ta mission est de concevoir un Atelier de Compréhension de Texte (ACT) à partir du document fourni.
    
    Structure de la réponse :
    1. ANALYSE DU SUPPORT : Obstacles de compréhension (inférences, lexique), intentions des personnages.
    2. PHASE 1 : Consignes de lecture individuelle.
    3. PHASE 2 (Émergence) : Propose 3 questions ouvertes pour lancer le débat.
    4. TABLEAU DÉBAT : Génère un tableau avec 3 affirmations 'D'accord / Pas d'accord / On ne sait pas'.
    5. PHASE 3 (Arbitrage) : Comment guider les élèves vers la preuve dans le texte.
    6. PHASE 4 (Métacognition) : Stratégie de lecture travaillée.
    
    IMPORTANT : Ne recopie pas l'intégralité du texte original par respect des droits d'auteur.
    """
    
    if "Cycle 2" in cycle:
        return base_prompt + "\nCONSIGNE SPÉCIFIQUE CYCLE 2 : Focalise sur la chronologie et les sentiments explicites."
    else:
        return base_prompt + "\nCONSIGNE SPÉCIFIQUE CYCLE 3 : Focalise sur l'implicite complexe et les intentions cachées."

# --- 6. TRAITEMENT ET GÉNÉRATION ---
if uploaded_file is not None:
    if st.button("Générer la fiche pédagogique"):
        with st.spinner('Analyse pédagogique en cours...'):
            try:
                prompt_final = obtenir_prompt(cycle_choisi)
                
                # Préparation du contenu pour l'IA
                if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(uploaded_file)
                    text_content = "\n".join([p.text for p in doc.paragraphs])
                    content = [prompt_final, f"Voici le texte à analyser :\n{text_content}"]
                else:
                    # PDF ou Images
                    file_data = uploaded_file.read()
                    content = [prompt_final, {"mime_type": uploaded_file.type, "data": file_data}]

                # Appel à l'IA
                response = model.generate_content(content)

                if response.text:
                    st.success("✅ Fiche générée avec succès !")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                    # Option de téléchargement
                    st.download_button(
                        label="📥 Télécharger la fiche (Texte)",
                        data=response.text,
                        file_name=f"ACT_ROLL_{cycle_choisi.split()[0]}.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")

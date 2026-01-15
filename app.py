import streamlit as st
import google.generativeai as genai
import os

# --- 1. INTERFACE (Placée au début pour qu'elle s'affiche toujours) ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")
st.title("🤖 Expert ROLL : Générateur d'ACT")

cycle_choisi = st.radio(
    "Pour quel niveau souhaitez-vous préparer cet ACT ?",
    ["Cycle 2 (CP, CE1, CE2)", "Cycle 3 (CM1, CM2, 6ème)"],
    index=0
)

uploaded_file = st.file_uploader("Chargez votre texte (Image, PDF ou Word)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

# --- 2. CONFIGURATION DE L'IA (Se lance seulement quand on clique) ---
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.info("👋 Bienvenue ! Veuillez configurer la clé API dans les Secrets pour activer l'analyse.")
    st.stop()

# Initialisation de la configuration
genai.configure(api_key=api_key)

# --- 3. TRAITEMENT ---
if uploaded_file is not None:
    if st.button("Générer la fiche pédagogique"):
        with st.spinner('L\'IA analyse votre document...'):
            try:
                # ASTUCE : On utilise le nom court sans préfixe pour éviter l'erreur 404
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Préparation du prompt
                prompt = f"Agis en tant qu'expert pédagogique du ROLL. Conçois un ACT pour le {cycle_choisi}. Analyse les obstacles, propose 3 questions d'émergence et un tableau débat. Ne recopie pas le texte."
                
                # Envoi selon le type de fichier
                if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    from docx import Document
                    doc = Document(uploaded_file)
                    text = "\n".join([p.text for p in doc.paragraphs])
                    response = model.generate_content([prompt, text])
                else:
                    img_data = uploaded_file.read()
                    response = model.generate_content([prompt, {"mime_type": uploaded_file.type, "data": img_data}])

                st.markdown("### Votre Fiche ACT :")
                st.write(response.text)
                
            except Exception as e:
                # Si l'erreur 404 revient, on propose une solution de secours automatique
                st.error(f"Erreur technique : {e}")
                st.info("Conseil : Allez dans requirements.txt et vérifiez que vous avez bien mis google-generativeai==0.8.3")

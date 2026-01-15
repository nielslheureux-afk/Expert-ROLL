import streamlit as st
import google.generativeai as genai
import os
from docx import Document

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖", layout="centered")

# --- 2. INTERFACE UTILISATEUR ---
st.title("🤖 Expert ROLL : Générateur d'ACT")
st.markdown("Outil d'intelligence artificielle pour concevoir des Ateliers de Compréhension de Texte.")

# Menu de sélection du cycle
cycle_choisi = st.radio(
    "Pour quel niveau scolaire ?",
    ["Cycle 2 (CP, CE1, CE2)", "Cycle 3 (CM1, CM2, 6ème)"],
    index=0
)

# Zone de dépôt de fichier
uploaded_file = st.file_uploader(
    "Chargez votre texte ou une photo du texte (JPG, PNG, PDF, DOCX)", 
    type=['pdf', 'docx', 'jpg', 'jpeg', 'png']
)

# --- 3. CONFIGURATION DE L'IA ---
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.info("👋 **Bienvenue !** Veuillez configurer votre `GEMINI_API_KEY` dans les **Secrets** de Streamlit pour commencer.")
    st.stop()

# Configuration stable
genai.configure(api_key=api_key)
# Utilisation du modèle 1.5-flash pour sa rapidité et sa capacité à lire les images
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 4. LOGIQUE DE GÉNÉRATION ---
if uploaded_file is not None:
    if st.button("🚀 Générer la fiche pédagogique"):
        with st.spinner('Analyse pédagogique en cours...'):
            try:
                # Définition du prompt pédagogique ROLL
                prompt = f"""Tu es un expert pédagogique spécialisé dans le ROLL (Réseau des Observatoires Local de la Lecture). 
                Ton objectif est de concevoir un Atelier de Compréhension de Texte (ACT) pour le {cycle_choisi}.
                
                La fiche doit contenir :
                1. ANALYSE DU TEXTE : Identification des obstacles (lexique, syntaxe, implicite).
                2. OBJECTIF : Ce que les élèves doivent comprendre.
                3. QUESTIONS D'ÉMERGENCE : 3 questions ouvertes pour lancer le débat.
                4. TABLEAU DÉBAT : Propose 3 affirmations (Vrai/Faux/On ne sait pas) pour confronter les interprétations.
                5. MÉTACOGNITION : Quelle stratégie de lecture est travaillée ?
                
                Réponds en français, de manière structurée et professionnelle."""

                # Extraction du contenu selon le type de fichier
                if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    # Cas d'un fichier Word
                    doc = Document(uploaded_file)
                    text_content = "\n".join([p.text for p in doc.paragraphs])
                    response = model.generate_content([prompt, f"Voici le texte à traiter :\n{text_content}"])
                
                else:
                    # Cas d'une image ou d'un PDF (Multimodal)
                    file_bytes = uploaded_file.read()
                    content_parts = [
                        prompt,
                        {"mime_type": uploaded_file.type, "data": file_bytes}
                    ]
                    response = model.generate_content(content_parts)

                # --- 5. AFFICHAGE DES RÉSULTATS ---
                if response.text:
                    st.success("✅ Votre fiche ACT est prête !")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                    # Option de téléchargement
                    st.download_button(
                        label="📥 Télécharger la fiche (Format Texte)",
                        data=response.text,
                        file_name=f"ACT_ROLL_{cycle_choisi.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )

            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")
                st.info("Si l'erreur est une '404', n'oubliez pas de Supprimer et Recréer l'application sur Streamlit pour mettre à jour la version de l'IA.")

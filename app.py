import streamlit as st
import google.generativeai as genai
import os
import io
from docx import Document

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

# On récupère la clé Gemini (assurez-vous qu'elle est dans vos Secrets)
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.title("Expert ROLL")
    st.info("Veuillez configurer la GEMINI_API_KEY dans les Secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. FONCTION WORD ---
def create_docx(text, cycle_name):
    doc = Document()
    doc.add_heading(f"Fiche ACT ROLL - {cycle_name}", 0)
    for line in text.split('\n'):
        clean_line = line.replace('*', '').replace('#', '').strip()
        if clean_line:
            doc.add_paragraph(clean_line)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. INTERFACE ---
st.title("Expert ROLL (Mode Haute Qualité)")
st.caption("Moteur : Gemini 1.5 Flash - Specialiste Pédagogie")

cycle = st.radio("Niveau scolaire :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Fichier Word (.docx)", type=['docx'])

if uploaded_file is not None:
    if st.button("Lancer l'analyse pédagogique"):
        with st.spinner('Gemini analyse les subtilités du texte...'):
            try:
                # Lecture Word
                doc_in = Document(uploaded_file)
                full_text = "\n".join([p.text for p in doc_in.paragraphs])

                # PROMPT EXPERT ROLL (Plus précis pour une meilleure qualité)
                prompt = f"""Tu es un expert du Réseau des Observatoires Locaux de la Lecture (ROLL). 
                Ton objectif est de créer un Atelier de Compréhension de Texte (ACT) de haute qualité pour le {cycle}.
                
                Consignes strictes :
                1. ANALYSE DES OBSTACLES : Identifie précisément les pièges du texte (implicite, lexique complexe, connecteurs logiques, culture de référence). Ne sois pas générique.
                2. QUESTIONS D'ÉMERGENCE : Propose 3 questions ouvertes qui forcent les élèves à confronter leurs représentations mentales.
                3. TABLEAU DÉBAT : Crée 4 affirmations subtiles (ni trop simples, ni impossibles) pour provoquer un débat interprétatif riche.
                
                TEXTE À ANALYSER :
                {full_text}
                """

                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown(response.text)
                
                docx_output = create_docx(response.text, cycle)
                st.download_button(
                    label="Télécharger en Word",
                    data=docx_output,
                    file_name="ACT_ROLL_Gemini.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            except Exception as e:
                if "429" in str(e):
                    st.error("Trop de demandes. Attends 60 secondes.")
                else:
                    st.error(f"Erreur : {e}")

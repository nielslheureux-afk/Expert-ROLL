import streamlit as st
from groq import Groq
import os
import io
from docx import Document

# --- CONFIGURATION ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

# --- INITIALISATION GROQ ---
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.info("Veuillez configurer la GROQ_API_KEY dans les Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# --- FONCTION WORD ---
def create_docx(text, cycle_name):
    doc = Document()
    doc.add_heading(f"Fiche ACT ROLL - {cycle_name}", 0)
    for line in text.split('\n'):
        if line.strip():
            doc.add_paragraph(line.replace('*', '').replace('#', ''))
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFACE ---
st.title("🤖 Expert ROLL (Moteur Llama 3)")
cycle = st.radio("Cycle :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Fichier texte (Word ou PDF)", type=['docx', 'pdf'])

if uploaded_file and st.button("🚀 Générer la fiche"):
    with st.spinner('Analyse pédagogique en cours...'):
        try:
            # Lecture du fichier Word
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc_in = Document(uploaded_file)
                content = "\n".join([p.text for p in doc_in.paragraphs])
            else:
                # Pour le PDF ou texte simple (fallback)
                content = uploaded_file.read().decode("utf-8", errors="ignore")

            prompt = f"""Tu es un expert pédagogique du ROLL. 
            Conçois un ACT pour le {cycle} à partir de ce texte. 
            Structure : Analyse des obstacles, 3 questions d'émergence, tableau de débat.
            Texte : {content}"""

            # Appel à Groq (Llama 3.3 70B est excellent)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-specdec",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            result = completion.choices[0].message.content
            
            st.markdown(result)
            
            # Bouton Word
            docx_buffer = create_docx(result, cycle)
            st.download_button("📥 Télécharger en Word", data=docx_buffer, file_name="ACT_ROLL.docx")

        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")

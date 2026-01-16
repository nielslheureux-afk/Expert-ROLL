import streamlit as st
from groq import Groq
import os
import io
from docx import Document

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

# --- 2. INITIALISATION ---
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.title("Expert ROLL")
    st.info("Veuillez configurer la GROQ_API_KEY dans les Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. FONCTION WORD ---
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

# --- 4. INTERFACE ---
st.title("Expert ROLL")
st.caption("Analyse pedagogique via Llama 3.3")

cycle = st.radio("Niveau scolaire :", ["Cycle 2", "Cycle 3"])
uploaded_file = st.file_uploader("Fichier Word (.docx)", type=['docx'])

# --- 5. GENERATION ---
if uploaded_file is not None:
    if st.button("Lancer la generation"):
        with st.spinner('Analyse en cours...'):
            try:
                # Lecture Word
                doc_in = Document(uploaded_file)
                full_text = "\n".join([p.text for p in doc_in.paragraphs])
                
                if len(full_text.strip()) < 5:
                    st.error("Document vide.")
                    st.stop()

                prompt = f"Expert ROLL. Concois un ACT pour le {cycle}. Analyse obstacles, 3 questions, tableau debat. Texte : {full_text}"

                # Appel Groq
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5
                )

                resultat = completion.choices[0].message.content
                st.markdown("---")
                st.markdown(resultat)
                
                # Telechargement
                docx_output = create_docx(resultat, cycle)
                st.download_button(
                    label="Telecharger en Word",
                    data=docx_output,
                    file_name="ACT_ROLL.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            except Exception as e:
                st.error(f"Erreur : {e}")

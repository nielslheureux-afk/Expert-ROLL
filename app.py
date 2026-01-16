import streamlit as st
import google.generativeai as genai
import os
import io
from docx import Document
from docx.shared import Pt, RGBColor

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Expert ROLL", page_icon="📖")

# --- 2. FONCTION DE CRÉATION DU DOCUMENT WORD ---
def create_docx(text, cycle_name):
    doc = Document()
    
    # Style de base : Arial 11
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    # Titre de la fiche
    title = doc.add_heading(f"Fiche ACT - {cycle_name}", 0)
    
    # Conversion du texte IA en paragraphes Word
    for line in text.split('\n'):
        clean_line = line.replace('*', '').replace('#', '').strip()
        if not clean_line:
            continue
            
        if line.startswith('#') or any(word.isupper() for word in line.split()[:2]) and len(line) < 50:
            # Titres de sections
            p = doc.add_heading(clean_line, level=1)
        elif line.strip().startswith(('-', '*', '•')):
            # Liste à puces
            p = doc.add_paragraph(clean_line, style='List Bullet')
        else:
            # Texte normal
            p = doc.add_paragraph(clean_line)
    
    # Sauvegarde en mémoire
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. GESTION DE L'IA & CLÉ API ---
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.title("🤖 Expert ROLL")
    st.info("Veuillez configurer votre clé API dans les Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def get_model():
    try:
        # Détection automatique du modèle disponible
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for candidate in ["models/gemini-3-flash", "models/gemini-2.0-flash", "models/gemini-1.5-flash"]:
            if candidate in available:
                return genai.GenerativeModel(candidate), candidate
        return genai.GenerativeModel(available[0]), available[0]
    except:
        return genai.GenerativeModel('gemini-1.5-flash'), "gemini-1.5-flash"

model, model_name = get_model()

# --- 4. INTERFACE UTILISATEUR ---
st.title("🤖 Expert ROLL")
st.caption(f"Propulsé par {model_name} | Quota : 1500 requêtes/jour")

cycle = st.radio("Niveau scolaire :", ["Cycle 2 (CP-CE2)", "Cycle 3 (CM1-6ème)"])
file = st.file_uploader("Document (Word, PDF, Image)", type=['docx', 'pdf', 'jpg', 'png'])

# --- 5. GÉNÉRATION ET TÉLÉCHARGEMENT ---
if file and st.button("🚀 Générer la fiche pédagogique"):
    with st.spinner('Analyse pédagogique ROLL...'):
        try:
            prompt = f"Expert ROLL. Conçois un ACT pour le {cycle}. Analyse obstacles, 3 questions, tableau débat."
            
            if file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc_in = Document(file)
                content = "\n".join([p.text for p in doc_in.paragraphs])
                response = model.generate_content([prompt, content])
            else:
                data = file.read()
                response = model.generate_content([prompt, {"mime_type": file.type, "data": data}])

            if response.text:
                st.success("✅ Analyse terminée !")
                
                # Aperçu à l'écran
                with st.expander("Voir l'aperçu de la fiche"):
                    st.markdown(response.text)
                
                # Création et téléchargement du Word
                docx_buffer = create_docx(response.text, cycle)
                
                st.download_button(
                    label="📥 Télécharger la fiche Word (Mise en page Pro)",
                    data=docx_buffer,
                    file_name=f"Fiche_ACT_{cycle.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        
        except Exception as e:
            st.error(f"Erreur : {e}")
            st.info("Astuce : Si une erreur 404 apparaît, redémarrez l'app dans les paramètres Streamlit.")

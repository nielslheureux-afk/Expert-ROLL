import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Expert ROLL", page_icon="📖")
st.title("🤖 Expert ROLL")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.warning("Ajoutez la clé dans Secrets.")
    st.stop()

# Configuration ultra-simple
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_file = st.file_uploader("Texte", type=['pdf', 'docx', 'png', 'jpg'])

if uploaded_file and st.button("Générer"):
    try:
        # Test direct
        response = model.generate_content("Analyse ce document pour un ACT ROLL")
        st.write(response.text)
    except Exception as e:
        st.error(f"Erreur persistante : {e}")

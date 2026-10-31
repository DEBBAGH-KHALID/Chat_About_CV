import streamlit as st
from cv_reader import lire_texte_cv
from llm import repondre
from audio import transcrire

st.set_page_config(page_title="CV Chat", page_icon="💬")
st.title("💬 Pose-moi des questions sur le CV")

# --- Mémoire de la session ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar ---

if st.sidebar.button("🗑️ Nouvelle conversation"):
    st.session_state.messages = []

# --- Upload du CV ---
fichier = st.file_uploader("Charge ton CV (PDF)", type="pdf")
if not fichier:
    st.info("Charge d'abord un PDF.")
    st.stop()

pdf_bytes = fichier.getvalue()

# Nouveau CV → on repart d'une conversation vide
if st.session_state.get("cv_nom") != fichier.name:
    st.session_state.cv_nom = fichier.name
    st.session_state.messages = []

texte_cv = lire_texte_cv(pdf_bytes)
if not texte_cv.strip():
    st.warning("Aucun texte trouvé : ton PDF est peut-être un scan (image). Il faudrait de l'OCR.")


def traiter(question):
    st.session_state.messages.append({"role": "user", "content": question})
    try:
        with st.spinner("Réflexion..."):
            texte, image = repondre(st.session_state.messages, texte_cv, pdf_bytes)
    except Exception as e:
        st.error(f"Erreur : {e}")
        st.session_state.messages.pop()  # on retire la question qui a échoué
        return
    st.session_state.messages.append({"role": "assistant", "content": texte, "image": image})
    st.rerun()


# --- Affichage de l'historique ---
for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m.get("image"):
            st.image(m["image"])
            st.download_button("Télécharger la photo", m["image"], "photo.png", "image/png", key=f"dl_{i}")

# --- Entrée vocale ---
audio = st.audio_input("🎤 Pose ta question en vocal")
if audio is not None:
    audio_bytes = audio.getvalue()
    audio_id = hash(audio_bytes)
    # Streamlit relit le même audio à chaque rerun : on ne le traite qu'une fois
    if st.session_state.get("dernier_audio") != audio_id:
        st.session_state.dernier_audio = audio_id
        with st.spinner("Transcription..."):
            question_vocale = transcrire(audio_bytes,"fr")
        if question_vocale:
            traiter(question_vocale)

# --- Entrée clavier ---
question = st.chat_input("Ou écris ta question...")
if question:
    traiter(question)
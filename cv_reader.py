import io
from pypdf import PdfReader


def lire_texte_cv(pdf_bytes):
    lecteur = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in lecteur.pages)
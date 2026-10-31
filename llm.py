from config import client, MODEL
from photo_tools import extraire_photo

SYSTEM_TEMPLATE = """Tu es un assistant qui répond aux questions sur un CV.
Réponds uniquement à partir du CV ci-dessous. Tu peux répondre aux salutations et à la conversation courante.
Si l'information n'est pas dans le CV, dis clairement : "Cette information n'est pas dans le CV".
N'invente rien. Réponds dans la langue de la question.
Si l'utilisateur demande la photo (photo de profil, image, portrait), utilise l'outil extraire_photo.

--- CV ---
{texte_cv}
"""

# La "carte des outils" que le LLM peut voir
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "extraire_photo",
            "description": "Extrait la photo de profil du CV. À utiliser quand l'utilisateur demande la photo.",
            "parameters": {"type": "object", "properties": {}},
        },
    }
]


def _historique_propre(messages):
    # On n'envoie à l'API que role + content (pas les images stockées côté interface)
    return [{"role": m["role"], "content": m["content"]} for m in messages]


def repondre(messages, texte_cv, pdf_bytes):
    """Retourne (texte, image_ou_None)."""
    reponse = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_TEMPLATE.format(texte_cv=texte_cv)}]
        + _historique_propre(messages),
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.2,
    )
    msg = reponse.choices[0].message

    # Le LLM veut utiliser un outil
    if msg.tool_calls:
        nom = msg.tool_calls[0].function.name
        if nom == "extraire_photo":
            photo = extraire_photo(pdf_bytes)
            if photo:
                return "Voici la photo extraite du CV.", photo
            return "Je n'ai trouvé aucune photo dans ce CV.", None

    return msg.content or "Je n'ai pas compris, peux-tu reformuler ?", None
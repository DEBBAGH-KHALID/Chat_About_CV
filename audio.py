from config import client, WHISPER_MODEL


def transcrire(audio_bytes, langue="fr"):
    resultat = client.audio.transcriptions.create(
        file=("question.wav", audio_bytes),
        model=WHISPER_MODEL,
        language=langue,
        response_format="text",
    )
    return (resultat if isinstance(resultat, str) else resultat.text).strip()
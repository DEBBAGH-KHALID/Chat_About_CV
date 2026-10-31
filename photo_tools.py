import fitz  # pymupdf
import cv2
import numpy as np


def _recadrer_visage(image, visage):
    """Coupe autour du visage avec une marge (utile si la photo est dans une grande image)."""
    x, y, w, h = visage
    h_img, w_img = image.shape[:2]
    x1 = max(0, x - int(w * 0.5))
    y1 = max(0, y - int(h * 0.5))
    x2 = min(w_img, x + w + int(w * 0.5))
    y2 = min(h_img, y + h + int(h * 0.8))
    return image[y1:y2, x1:x2]


def extraire_photo(pdf_bytes):
    """Retourne la photo de profil (bytes PNG) ou None si aucune photo trouvée."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    detecteur = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    for page in doc:
        for img in page.get_images(full=True):
            data = doc.extract_image(img[0])["image"]
            image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                continue

            gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            visages = detecteur.detectMultiScale(gris, 1.1, 5, minSize=(40, 40))
            if len(visages) == 0:
                continue

            # Le plus grand visage de l'image
            visage = max(visages, key=lambda v: v[2] * v[3])

            # Si le visage est petit par rapport à l'image → c'est une grande image, on recadre
            h_img, w_img = image.shape[:2]
            if (visage[2] * visage[3]) / (w_img * h_img) < 0.25:
                image = _recadrer_visage(image, visage)

            ok, png = cv2.imencode(".png", image)
            if ok:
                return png.tobytes()

    return None
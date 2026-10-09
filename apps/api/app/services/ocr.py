from io import BytesIO
from PIL import Image, UnidentifiedImageError
import pytesseract

def extract_text(data: bytes) -> str:
    try:
        image = Image.open(BytesIO(data)).convert('RGB')
    except UnidentifiedImageError as exc:
        raise ValueError('Invalid image file') from exc
    return pytesseract.image_to_string(image, lang='eng+ben')

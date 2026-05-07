import fitz  # PyMuPDF
import easyocr
import cv2
import numpy as np
import warnings

# Suppress annoying easyocr CPU warnings in the terminal
warnings.filterwarnings("ignore", category=UserWarning)

# Initialize EasyOCR globally (CPU mode for Streamlit Cloud compatibility)
reader = easyocr.Reader(['en'], gpu=False, verbose=False)

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Attempt to read native digital text first (super fast)
        text = page.get_text("text")

        if text.strip():
            full_text += text + "\n"
        else:
            # If empty, it's a scanned image. Boot up EasyOCR.
            pix = page.get_pixmap(dpi=150) # 150 DPI is a good balance of speed and clarity
            img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)

            # Convert to Grayscale
            if pix.n == 4:
                img_gray = cv2.cvtColor(img_data, cv2.COLOR_RGBA2GRAY)
            else:
                img_gray = cv2.cvtColor(img_data, cv2.COLOR_RGB2GRAY)

            # MAGIC CONTRAST BOOSTER: Forces pure white background and pure black text
            _, img_thresh = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)

            # Read text with EasyOCR
            results = reader.readtext(img_thresh)
            for (bbox, text, prob) in results:
                full_text += text + " "
            full_text += "\n"

    return full_text
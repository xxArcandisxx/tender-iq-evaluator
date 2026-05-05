import fitz  # PyMuPDF
import numpy as np
import cv2
import easyocr

# Initialize the EasyOCR engine (gpu=False ensures it doesn't crash on Streamlit Cloud later)
ocr_engine = easyocr.Reader(['en'], gpu=False)

def extract_text_with_coordinates(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_data = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Calculate our "Safe Zones" to strip headers and footers
        page_height = page.rect.height
        top_margin = page_height * 0.08
        bottom_margin = page_height * 0.92
        
        # Try normal text extraction first (Fast Path)
        raw_text = page.get_text("text").strip()
        
        if raw_text:
            # It's a normal, digital PDF!
            blocks = page.get_text("blocks")
            for b in blocks:
                x0, y0, x1, y1, text, block_no, block_type = b
                if block_type == 0:
                    text_content = text.strip()
                    if text_content and y0 > top_margin and y1 < bottom_margin:
                        extracted_data.append({
                            "page": page_num + 1,
                            "text": text_content,
                            "bbox": [x0, y0, x1, y1]
                        })
        else:
            # SCANNED PDF DETECTED! (Slow Path: EasyOCR)
            print(f"Page {page_num + 1} appears to be scanned. Booting up EasyOCR...")
            
            # 1. Take a high-res screenshot
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
            
            # 2. Convert to standard RGB
            if pix.n == 4: 
                img_data = cv2.cvtColor(img_data, cv2.COLOR_RGBA2RGB)
            elif pix.n == 1:
                img_data = cv2.cvtColor(img_data, cv2.COLOR_GRAY2RGB)
                
            # 3. Read the text with EasyOCR
            result = ocr_engine.readtext(img_data)
            
            for line in result:
                coords = line[0]  # EasyOCR gives 4 corner coordinates
                text_content = line[1]
                
                # Get the Y coordinate of the top-left corner
                y0 = coords[0][1] / 2 # Divide by 2 because of our 2x zoom earlier
                
                # Apply our header/footer filter
                if text_content and y0 > top_margin and y0 < bottom_margin:
                    extracted_data.append({
                        "page": page_num + 1,
                        "text": text_content,
                        "bbox": "OCR_Generated"
                    })

    return extracted_data

if __name__ == "__main__":
    test_data = extract_text_with_coordinates("sample_bid.pdf")
    print(f"Extracted {len(test_data)} blocks of text!")
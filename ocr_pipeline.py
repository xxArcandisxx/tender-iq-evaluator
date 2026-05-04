import fitz  # PyMuPDF

def extract_text_with_coordinates(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_data = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Calculate our "Safe Zones" to strip headers and footers
        page_height = page.rect.height
        top_margin = page_height * 0.08
        bottom_margin = page_height * 0.92
        
        blocks = page.get_text("blocks")

        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            
            if block_type == 0:
                text_content = text.strip()
                
                # If text exists and is inside the safe zone, save it
                if text_content and y0 > top_margin and y1 < bottom_margin:
                    extracted_data.append({
                        "page": page_num + 1,
                        "text": text_content,
                        "bbox": [x0, y0, x1, y1]
                    })
                    
    return extracted_data

if __name__ == "__main__":
    test_data = extract_text_with_coordinates("sample_bid.pdf")
    print(f"Extracted {len(test_data)} clean text blocks. Headers and footers removed!")
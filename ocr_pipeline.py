import fitz  # PyMuPDF

def extract_text_with_coordinates(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_data = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Get the total height of the page to calculate our "Safe Zones"
        page_height = page.rect.height
        
        # Define our margins: Ignore the top 8% and bottom 8% of every page
        top_margin = page_height * 0.08
        bottom_margin = page_height * 0.92
        
        # Extract text blocks
        blocks = page.get_text("blocks")

        for b in blocks:
            # PyMuPDF block format: (x0, y0, x1, y1, "text", block_no, block_type)
            x0, y0, x1, y1, text, block_no, block_type = b
            
            # block_type 0 is text. block_type 1 is images. We only want text.
            if block_type == 0:
                text_content = text.strip()
                
                # --- THE SMART FILTER ---
                # 1. Is there actually text?
                # 2. Is it below the top margin? (Not a header)
                # 3. Is it above the bottom margin? (Not a footer/page number)
                if text_content and y0 > top_margin and y1 < bottom_margin:
                    extracted_data.append({
                        "page": page_num + 1,
                        "text": text_content,
                        "bbox": [x0, y0, x1, y1]
                    })
                    
    return extracted_data

# Optional: You can run this file directly to test the smart extraction
if __name__ == "__main__":
    test_data = extract_text_with_coordinates("sample_bid.pdf")
    print(f"Extracted {len(test_data)} clean text blocks. Headers and footers removed!")
import fitz  # This is PyMuPDF
import json

def extract_text_with_coordinates(pdf_path):
    print(f"Reading document: {pdf_path}...\n")
    doc = fitz.open(pdf_path)
    extracted_data = []

    # Loop through every page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # get_text("blocks") pulls paragraphs AND their exact x,y coordinates!
        blocks = page.get_text("blocks")
        
        for b in blocks:
            # block format: (x0, y0, x1, y1, "text", block_no, block_type)
            # block_type 0 means it is text, not an image
            if b[6] == 0:  
                text_content = b[4].strip()
                # Ignore empty spaces
                if text_content: 
                    extracted_data.append({
                        "page": page_num + 1,
                        "text": text_content,
                        # [x0, y0, x1, y1] coordinates
                        "bbox": [round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)]
                    })

    return extracted_data

if __name__ == "__main__":
    pdf_filename = "sample_tender.pdf"
    
    try:
        data = extract_text_with_coordinates(pdf_filename)
        
        # Let's print just the first 3 blocks so we don't flood your terminal
        print("--- EXTRACTED BLOCKS (FIRST 3) ---")
        print(json.dumps(data[:3], indent=4))
        
        print(f"\nSuccess! Total text blocks extracted: {len(data)}")
        print("Notice how every piece of text now has exact coordinates? That's your Evidence Layer!")
        
    except FileNotFoundError:
        print(f"❌ ERROR: I couldn't find a file named '{pdf_filename}'. Did you put one in the folder?")
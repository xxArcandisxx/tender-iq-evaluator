import os
import json
from dotenv import load_dotenv
from groq import Groq

# Import the OCR function you just wrote!
from ocr_pipeline import extract_text_with_coordinates

# Load your secret keys
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def extract_verifiable_rules(pdf_path):
    print(f"1. Extracting text and coordinates from {pdf_path}...")
    
    # Run the PDF through your PyMuPDF eyes
    ocr_blocks = extract_text_with_coordinates(pdf_path)
    
    print("2. Sending structured data to Groq Llama 3.1 for analysis...\n")
    
    # We pass the OCR data directly into the prompt
    prompt = f"""
    You are a strict legal data extraction AI. 
    I am giving you an array of text blocks extracted from a tender document. Each block has "text", "page", and "bbox" (bounding box coordinates).
    
    Your job is to extract the compliance criteria. 
    You MUST output valid JSON only. Output a JSON object with a key "criteria" containing an array of objects. 
    Each object must have:
    - "rule_name" (e.g., Minimum Turnover)
    - "required_value" (e.g., 12.5 Crores)
    - "category" (Financial, Technical, or Legal)
    - "evidence_link": an object containing the "page" and "bbox" array of the exact text block where you found this rule.
    
    Here are the document blocks:
    {json.dumps(ocr_blocks)}
    """

    # Call the cloud AI
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You output JSON only."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.1-8b-instant",
        temperature=0, 
        response_format={"type": "json_object"} 
    )

    return chat_completion.choices[0].message.content

if __name__ == "__main__":
    # Run the engine on your dummy tender
    result = extract_verifiable_rules("sample_tender.pdf")
    
    # Parse and print the final structured output
    parsed_json = json.loads(result)
    print("--- FINAL EVALUATION REPORT WITH EVIDENCE LINKS ---")
    print(json.dumps(parsed_json, indent=4))
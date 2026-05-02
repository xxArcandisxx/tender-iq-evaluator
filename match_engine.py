import os
import json
from dotenv import load_dotenv
from groq import Groq
from ocr_pipeline import extract_text_with_coordinates
from evaluator_engine import extract_verifiable_rules

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def evaluate_bidder_against_rules(tender_pdf_path, bidder_pdf_path):
    print("1. Extracting rules from Tender Document...")
    # This calls your original script!
    tender_rules_json = extract_verifiable_rules(tender_pdf_path)
    
    print("\n2. Extracting text from Bidder Submission...")
    bidder_blocks = extract_text_with_coordinates(bidder_pdf_path)
    
    print("\n3. Cross-referencing Bidder data against Tender rules using Groq AI...")
    
    prompt = f"""
    You are an expert procurement auditor. Your job is to strictly evaluate a Bidder's submission against the Tender Rules.
    
    TENDER RULES (JSON):
    {tender_rules_json}
    
    BIDDER DOCUMENT BLOCKS (JSON):
    {json.dumps(bidder_blocks)}
    
    Instructions:
    Compare the Bidder Document against EVERY rule in the Tender Rules.
    For each rule, determine if the bidder Passed, Failed, or needs to be Flagged (if the data is ambiguous).
    
    You MUST output valid JSON only. Output a JSON object with a key "evaluation_results" containing an array. 
    Each object in the array must have:
    - "rule_name": the name of the rule
    - "tender_requirement": what the tender asked for
    - "bidder_submission": what the bidder actually provided (or "Not found")
    - "status": "Pass", "Fail", or "Flagged"
    - "reasoning": A one-sentence explanation of why they passed/failed
    """

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
    result = evaluate_bidder_against_rules("sample_tender.pdf", "sample_bid.pdf")
    
    parsed_json = json.loads(result)
    print("\n\n=======================================================")
    print("              FINAL BIDDER EVALUATION REPORT             ")
    print("=======================================================")
    print(json.dumps(parsed_json, indent=4))
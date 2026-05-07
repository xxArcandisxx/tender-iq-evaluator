import os
import json
from groq import Groq
from dotenv import load_dotenv
from ocr_pipeline import extract_text_from_pdf

# Load the environment variables from your .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def evaluate_bidder_against_rules(tender_path, bidder_path):
    # Extract text from both documents using our custom pipeline
    tender_text = extract_text_from_pdf(tender_path)
    bidder_text = extract_text_from_pdf(bidder_path)

    prompt = f"""
    You are an expert government procurement auditor. You are evaluating a Bidder's submission against the Master Tender Rules.

    TENDER RULES:
    {tender_text}

    BIDDER DOCUMENT:
    {bidder_text}

    INSTRUCTIONS:
    1. Extract all mandatory specifications or rules from the TENDER RULES.
    2. Compare the BIDDER DOCUMENT against EVERY rule.
    3. Output a STRICT JSON object containing an "evaluation_results" array.
    4. CRITICAL: You MUST provide a detailed "reasoning" paragraph for EVERY SINGLE RULE. Do not leave any reasoning blank.

    JSON OUTPUT FORMAT:
    {{
        "evaluation_results": [
            {{
                "rule_name": "Brief Title of the Rule",
                "tender_requirement": "What did the tender strictly ask for?",
                "bidder_submission": "Summarize what the bidder provided for this specific rule.",
                "status": "Pass" or "Fail" or "Flagged",
                "score": <integer from 1 to 5>,
                "reasoning": "MANDATORY: Step-by-step logical explanation of exactly why this score was given.",
                "exact_quote": "The verbatim sentence extracted from the bidder document."
            }}
        ]
    }}
    """

    # Force Groq to return guaranteed JSON using JSON mode
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a strict procurement AI that outputs ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1 # Low temperature for analytical strictness
    )

    return response.choices[0].message.content
import os
import json
from dotenv import load_dotenv
from groq import Groq

# Load keys from the .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Fake text simulating a scanned tender document
sample_tender_text = """
SECTION 4: ELIGIBILITY CRITERIA
1. The bidding company must have a minimum average annual turnover of ₹5.5 Crores over the last three financial years.
2. The bidder must provide a valid ISO 9001:2015 quality management certificate.
3. An Earnest Money Deposit (EMD) of ₹2,50,000 must be submitted via Demand Draft.
4. The bidder must not have been blacklisted by any Government department.
"""

def extract_tender_rules(text):
    print("Sending text to Groq Llama 3.1...")
    
    prompt = f"""
    You are a strict legal data extraction AI. 
    Read the following tender document text and extract the compliance criteria.
    
    You MUST output valid JSON only. Output a JSON object with a key "criteria" containing an array of objects. 
    Each object must have the keys: "rule_name", "required_value", and "category" (Financial, Technical, or Legal).
    
    Document Text:
    {text}
    """

    # We use Llama 3.1 8B on Groq because it is blazingly fast
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You output JSON only."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.1-8b-instant",
        temperature=0, # 0 means we want factual, deterministic answers, not creative ones
        response_format={"type": "json_object"} # Forces Groq to guarantee JSON output
    )

    return chat_completion.choices[0].message.content

if __name__ == "__main__":
    # Run the function
    result = extract_tender_rules(sample_tender_text)
    
    # Parse and print beautifully
    parsed_json = json.loads(result)
    print(json.dumps(parsed_json, indent=4))
# ⚖️ Tender IQ Evaluator

**AI-powered procurement evaluation for faster, clearer tender decisions.**

Tender IQ Evaluator helps procurement teams compare bidder submissions against tender requirements. It extracts requirements from tender PDFs, analyzes bidder documents with AI, and presents transparent Pass, Fail, or Flagged results with scores, reasoning, and supporting quotes.

## Features

- Upload one tender or RFP document
- Upload multiple bidder proposals for comparison
- Extract text from digital and scanned PDFs
- Use OCR for scanned documents with EasyOCR
- Identify financial, technical, and legal requirements
- Evaluate every bidder against every extracted rule
- Generate Pass, Fail, or Flagged compliance results
- Include scores, explanations, and exact bidder-document quotes
- Compare bidders through an interactive Streamlit dashboard
- Rank and summarize bidder performance

## How It Works

1. Upload the official tender document.
2. Upload one or more bidder submissions.
3. Tender IQ extracts the tender requirements and bidder content.
4. Groq's Llama model compares each submission against every requirement.
5. The dashboard displays bidder scores, compliance status, reasoning, and evidence.

## Tech Stack

- **Interface:** Streamlit
- **AI evaluation:** Groq API with Llama 3.1
- **PDF extraction:** PyMuPDF
- **OCR:** EasyOCR, OpenCV, and NumPy
- **Language:** Python 3.8+
- **Optional backend services:** Supabase and FastAPI dependencies are included for future extensions

## Run Locally

### Prerequisites

- Python 3.8 or newer
- A [Groq API key](https://console.groq.com/keys)
- Visual C++ Build Tools on Windows if PyMuPDF or OCR dependencies require them

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/xxArcandisxx/tender-iq-evaluator.git
   cd tender-iq-evaluator
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   ```

   Windows:

   ```bash
   .\venv\Scripts\activate
   ```

   macOS/Linux:

   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create an environment file:

   ```bash
   cp env_example .env
   ```

   On Windows PowerShell:

   ```powershell
   Copy-Item env_example .env
   ```

5. Add your Groq API key to `.env`:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

6. Start the dashboard:

   ```bash
   streamlit run app.py
   ```

7. Open the local URL shown by Streamlit, usually [http://localhost:8501](http://localhost:8501).

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `GROQ_API_KEY` | Yes | API key used for requirement extraction and bidder evaluation |

Never commit `.env` or any file containing a real API key. Keep credentials local or configure them through your deployment provider's secrets manager.

## Project Structure

```text
tender-iq-evaluator/
├── app.py                 # Streamlit dashboard and upload workflow
├── evaluator_engine.py    # Tender requirement extraction with evidence links
├── match_engine.py        # Bidder-to-tender evaluation engine
├── ocr_pipeline.py        # Digital PDF extraction and scanned PDF OCR
├── requirements.txt       # Python dependencies
├── env_example            # Environment variable template
└── *.pdf                  # Sample tender and bidder documents
```

## Important Notes

- The application is an AI-assisted review tool, not a substitute for legal or procurement expertise.
- Always verify flagged results and generated reasoning against the original documents.
- OCR quality depends on scan resolution, document layout, and image clarity.
- Groq API usage may be subject to rate limits and provider availability.
- Uploaded documents are processed by the local application and the extracted text sent to Groq for analysis.

## Sample Documents

The repository includes sample tender and bidder PDFs for local testing. Use them to understand the evaluation workflow before uploading production documents.

## Contributing

1. Create a feature branch.
2. Make focused changes.
3. Run the application locally and test with sample PDFs.
4. Open a pull request with a clear description of the change.

## License

No license has been specified for this project yet.

# ⚖️ Tender IQ: AI Procurement Evaluator

**Automated, transparent compliance checking for government tenders.**

Tender IQ is an AI-powered legal document evaluation engine. It automatically extracts compliance criteria from complex government Tender Documents (NITs) and cross-references them against Bidder Submissions to provide a verifiable, color-coded Pass/Fail/Flagged analysis.

## 🚀 Key Features

* **Intelligent Rule Extraction:** Uses Groq (Llama 3.1) to parse complex legal text into structured JSON criteria.
* **Evidence Linking (OCR):** Powered by PyMuPDF, the engine maps every extracted rule to exact `[x, y, w, h]` bounding box coordinates on the original document.
* **Smart Bidder Matching:** Employs Two-Way RAG (Retrieval-Augmented Generation) logic to catch human loopholes (e.g., distinguishing between an "active" vs. "applied for" ISO certificate).
* **Interactive Dashboard:** Built with Streamlit for a clean, side-by-side evidence verification UI.

## 🛠️ Tech Stack

* **Frontend/UI:** Streamlit
* **AI/LLM Engine:** Groq API (Llama-3.1-8b-instant)
* **Document Processing:** PyMuPDF (fitz)
* **Backend:** Python 3.10+

---

## 💻 Local Setup Instructions

Follow these steps to run the Tender IQ Evaluator on your local machine.

### 1. Prerequisites
* Python 3.8 or higher installed on your machine.
* A free [Groq API Key](https://console.groq.com/keys).
* *Windows Users:* Ensure you have [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) installed (required for PyMuPDF).

### 2. Clone the Repository
Open your terminal and run:
```bash
git clone [https://github.com/YourUsername/tender-iq-evaluator.git](https://github.com/YourUsername/tender-iq-evaluator.git)
cd tender-iq-evaluator](https://github.com/xxArcandisxx/tender-iq-evaluator.git)

Set Up the Virtual Environment
ython -m venv venv

# Activate on Windows:
.\venv\Scripts\activate

# Activate on Mac/Linux:
source venv/bin/activate

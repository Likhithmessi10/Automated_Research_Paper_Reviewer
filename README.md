# 📝 PaperLens – Expert AI Research Paper Reviewer

**PaperLens** is a state-of-the-art **Hybrid AI Review System** that combines fast heuristic analysis with deep Large Language Model (LLM) reasoning. It is designed to replicate the analytical rigor of an expert peer reviewer at top-tier conferences like **NeurIPS** or **ICML**.

The system analyzes research papers (PDF) to provide:
- 🧠 **NeurIPS-Style Expert Scorecard** (Originality, Methodology, Clarity, Significance)
- 🔍 **Deep Semantic Section Analysis** (Critiquing Logic & Experiments)
- ✅ **Heuristic Strength & Weakness Detection** (Pattern Matching)
- 📊 **Plagiarism & Originality Risk Assessment**
- ✍️ **AI-Powered Academic Rewriting** (Professional Tone Polish)

Built as a **Final Year CSE (AI/ML) Project**, this tool helps researchers, students, and reviewers automate the initial phase of academic evaluation.

---

## 🚀 Key Features

### 🌟 New in v2 (Expert AI Engine)
- **Hybrid Architecture:** Merges instant keyword analysis (v1) with deep Llama-3 reasoning (v2).
- **Expert Scorecard:** Quantitative 1-10 scoring on **Originality**, **Methodology**, **Clarity**, and **Significance**.
- **Deep Section Critique:** Reads the full *Methodology* and *Results* sections to find logical gaps, missing baselines, or weak arguments.
- **Smart Score Sync:** Automatically aligns top-level scores with deep-dive section evaluations.

### ⚡ Core Features
- **PDF Parsing:** Automatic extraction and section segmentation (Abstract, Intro, Methods, etc.).
- **Instant NLP Analysis:** Uses spaCy to detect sentence-level strengths and weaknesses.
- **Plagiarism Check:** Online search integration to estimate originality and risk.
- **AI Rewriting:** Uses local **Ollama (Llama 3.1)** to rewrite informal sentences into professional academic English.
- **Interactive Dashboard:** Modern Streamlit UI with Plotly charts and side-by-side text comparisons.
- **Mobile-Ready API:** FastAPI backend to serve Android/iOS clients.

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit (Web Dashboard)
- **Backend Logic:** Python 3.x
- **LLM Engine:** Ollama (running Llama 3.1:8b locally)
- **API:** FastAPI + Uvicorn
- **NLP:** spaCy (`en_core_web_sm`)
- **PDF Processing:** PyMuPDF (`fitz`)
- **Data Visualization:** Plotly & Pandas
- **Plagiarism:** Custom Google Search Heuristics

---

## 📁 Project Structure

```bash
Automated_Research_paper_reviewer/
│
├── api.py               # FastAPI backend for Mobile/Web integration
├── frontend.py          # Streamlit Dashboard (v2 with Scorecards)
├── review_model.py      # Core Hybrid Logic (Heuristics + Llama 3 Analysis)
├── online_plagiarism.py # Plagiarism detection module
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## ✅ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Likhithmessi10/Automated_Research_Paper_Reviewer 
cd Automated_Research_Paper_Reviewer
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3️⃣ Setup Ollama (Crucial for v2 Features)
1. Download [Ollama](https://ollama.com).
2. Start the server:
   ```bash
   ollama serve
   ```
3. Pull the Llama 3 model (required for Expert Review):
   ```bash
   ollama pull llama3.1:8b
   ```

### 4️⃣ Run the Application

**Option A: Interactive Dashboard (Streamlit)**
```bash
streamlit run frontend.py
```
*Opens in browser at `http://localhost:8501`*

**Option B: REST API (For Mobile Apps)**
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```
*API Docs available at `http://localhost:8000/docs`*

---

## 📊 Dashboard Overview

The **PaperLens Dashboard** provides a comprehensive report:

1.  **Expert Scorecard (v2):**
    * **Originality (1-10):** How novel is the approach?
    * **Methodology (1-10):** Are the experiments rigorous?
    * **Recommendation:** Accept / Weak Accept / Reject.
    * **Reasoning:** A generated summary of *why* the decision was made.

2.  **Deep Section Analysis:**
    * **Methodology Review:** Summarizes the technical approach and lists specific semantic weaknesses.
    * **Results Review:** Critiques the experimental validity.

3.  **Heuristic Insights (v1):**
    * Lists of specific "Strength" and "Weakness" sentences found in the text.
    * Plagiarism Risk Meter.

4.  **AI Rewriting:**
    * Side-by-side comparison of original text vs. AI-polished professional version.

---

## 🔌 API Usage (Mobile Integration)

You can send a PDF to the backend to get the JSON report (used by the PaperLens Mobile App).

**Endpoint:** `POST /analyze`

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@research_paper.pdf" \
  -F "rewrite=true"
```

**Response (JSON):**
```json
{
  "verdict": "Weak Accept",
  "final_card": {
    "originality": 8,
    "methodology": 7,
    "recommendation": "Weak Accept"
  },
  "methodology_review": { ... },
  "report": "..."
}
```

---

## 🔮 Future Enhancements

- 🧠 **Journal-Specific Fine-tuning:** Adapt scoring for IEEE vs. Nature.
- ⚡ **Cloud LLM Support:** Option to switch from local Ollama to GPT-4/Claude API.
- 📱 **Native Mobile App:** Flutter-based interface for on-the-go reviews.
- 🏳️ **Multi-Language Reviews:** Support for non-English papers.

---

## 👨‍💻 Developed By

**Team:** PaperLens  
**Stream:** CSE (AI & ML)  
**Project:** Final Year Major Project (2025)

---

## 📜 License

This project is intended for educational and research purposes.
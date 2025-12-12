# 📝 Automated Research Paper Reviewer

**Automated Research Paper Reviewer** is a state-of-the-art **Hybrid AI Review System** that combines fast heuristic analysis with deep Large Language Model (LLM) reasoning. It is designed to replicate the analytical rigor of an expert peer reviewer at top-tier conferences like **NeurIPS** or **ICML**.

The system analyzes research papers (PDF) to provide:
- 🧠 **NeurIPS-Style Expert Scorecard** (Originality, Methodology, Clarity, Significance)
- 🔍 **Deep Semantic Section Analysis** (Critiquing Logic & Experiments)
- ✅ **Heuristic Strength & Weakness Detection** (Pattern Matching)
- 📊 **Plagiarism & Originality Risk Assessment**
- ✍️ **AI-Powered Academic Rewriting** (Professional Tone Polish)

Built as a **Final Year CSE (AI/ML) Project**, this tool helps researchers, students, and reviewers automate the initial phase of academic evaluation.

---

## 📋 Table of Contents

- [🚀 Key Features](#-key-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Project Structure](#-project-structure)
- [✅ Installation & Setup](#-installation--setup)
- [📊 Dashboard Overview](#-dashboard-overview)
- [🔌 API Usage](#-api-usage-mobile-integration)
- [💡 Usage Examples](#-usage-examples)
- [🔧 Configuration & Customization](#-configuration--customization)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📚 References & Acknowledgments](#-references--acknowledgments)
- [📞 Support & Contact](#-support--contact)
- [🔮 Future Enhancements](#-future-enhancements)
- [👨‍💻 Developed By](#-developed-by)
- [📜 License](#-license)

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
├── api.py                    # FastAPI backend for Mobile/Web integration
├── server.py                 # Alternative FastAPI server implementation
├── frontend.py               # Streamlit Dashboard (v2 with Scorecards)
├── review_model.py           # Core Hybrid Logic (Heuristics + Llama 3 Analysis)
├── online_plagiarism.py      # Plagiarism detection module
├── phase1.md                 # Project requirements and user personas documentation
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── .gitignore               # Git ignore rules
├── .streamlit/              # Streamlit configuration
│   └── config.toml          # Streamlit app configuration
├── venv/                    # Virtual environment (optional)
└── __pycache__/             # Python cache files
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

## 🚀 Quick Start (5 Minutes)

1. **Download a sample PDF** or use your own research paper
2. **Start Ollama** (if using AI features): `ollama serve && ollama pull llama3.1:8b`
3. **Launch the app**: `streamlit run frontend.py`
4. **Upload your PDF** and click "Analyze Paper"
5. **Review the results**: Check the expert scorecard, deep analysis, and AI suggestions

**Expected Output:** A comprehensive report with scores, recommendations, and rewritten sections.

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

## 💡 Usage Examples

### **Example 1: Student Paper Review**
A student submits their first research paper on machine learning:

**Input:** `student_paper.pdf` (5-page undergraduate thesis)

**Output:**
- **Verdict:** Weak Accept
- **Originality Score:** 6/10 (Some novel ideas but builds on existing work)
- **Methodology Score:** 5/10 (Basic experiments, missing ablation studies)
- **AI Suggestions:** "Consider adding baseline comparisons" and "Rewrite introduction for clarity"

### **Example 2: Conference Paper Evaluation**
A professor reviews submissions for ICML:

**Input:** `icml_submission.pdf` (12-page conference paper)

**Output:**
- **Verdict:** Accept
- **Originality Score:** 9/10 (Novel approach with strong theoretical contribution)
- **Methodology Score:** 8/10 (Rigorous experiments with proper baselines)
- **Deep Analysis:** "Methodology section shows excellent experimental design"

### **Example 3: Plagiarism Detection**
System detects potential plagiarism in a submitted paper:

**Input:** `suspicious_paper.pdf`

**Output:**
- **Plagiarism Risk:** HIGH (45% detected)
- **Verdict:** ❌ REJECT (PLAGIARISM)
- **Originality Score:** 55%
- **Flagged Sentences:** 3 out of 5 sample sentences found online

---

## 🔧 Configuration & Customization

## � Configuration & Customization

### **Ollama Model Settings**
You can customize the AI model used for deep analysis:

```python
# In review_model.py, modify these parameters:
OLLAMA_MODEL = "llama3.1:8b"  # or "mistral:7b", "codellama:13b"
OLLAMA_TIMEOUT = 60  # seconds
OLLAMA_TEMPERATURE = 0.1  # lower = more consistent
```

### **Scoring Thresholds**
Adjust the acceptance criteria in `review_model.py`:

```python
# Confidence thresholds for verdicts
ACCEPT_THRESHOLD = 0.65      # >65% = Accept
WEAK_ACCEPT_THRESHOLD = 0.45  # 45-65% = Weak Accept
# <45% = Reject
```

### **Plagiarism Sensitivity**
Configure plagiarism detection in `online_plagiarism.py`:

```python
# Number of sentences to sample for checking
SAMPLE_SIZE = 3
# Risk threshold for auto-rejection
PLAGIARISM_REJECT_THRESHOLD = 40  # %
```

---

## 🐛 Troubleshooting

### **Common Issues & Solutions**

**❌ Ollama Connection Failed**
```
Error: Connection refused on localhost:11434
```
**Solution:**
1. Ensure Ollama is running: `ollama serve`
2. Check if the model is downloaded: `ollama list`
3. Pull the model if missing: `ollama pull llama3.1:8b`
4. Verify firewall allows local connections

**❌ spaCy Model Not Found**
```
Error: Can't find model 'en_core_web_sm'
```
**Solution:**
```bash
python -m spacy download en_core_web_sm
```

**❌ PDF Processing Failed**
```
Error: PDF parsing error
```
**Solution:**
- Ensure PDF is not password-protected
- Check if PDF is corrupted or scanned (OCR required)
- Verify PyMuPDF installation: `pip install --upgrade PyMuPDF`

**❌ Streamlit Port Already in Use**
```
Error: Port 8501 is already in use
```
**Solution:**
```bash
# Use a different port
streamlit run frontend.py --server.port 8502
```

**❌ FastAPI CORS Issues (Mobile App)**
```
Error: CORS policy blocked
```
**Solution:** Add CORS middleware in `api.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### **Development Setup**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Set up development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

### **Code Standards**
- Follow PEP 8 style guidelines
- Add type hints for function parameters
- Write docstrings for all functions
- Add unit tests for new features

### **Testing**
```bash
# Run basic functionality tests
python -c "from review_model import review_pdf; print('Import successful')"

# Test API endpoints
python -c "import requests; print(requests.get('http://localhost:8000').status_code)"
```

### **Pull Request Process**
1. Update the README.md with details of changes
2. Update version numbers in any examples files
3. The PR will be merged after review and testing

---

## 📚 References & Acknowledgments

### **Academic References**
- **NeurIPS Review Criteria:** Based on official NeurIPS reviewer guidelines
- **ICML Scoring Rubrics:** Adapted from ICML conference review forms
- **Academic Writing Standards:** Following APA and IEEE style guides

### **Technical References**
- **spaCy Documentation:** Natural Language Processing library
- **PyMuPDF (Fitz):** PDF text extraction
- **Ollama:** Local LLM inference framework
- **FastAPI:** Modern Python web framework

### **Inspiration**
- **PeerReview.io:** Academic peer review platform
- **OpenReview.net:** Open peer review system
- **Grammarly for Academia:** AI writing assistance

---

## 📞 Support & Contact

- **Repository:** [GitHub](https://github.com/Likhithmessi10/Automated_Research_Paper_Reviewer)
- **Issues:** [Report Bugs](https://github.com/Likhithmessi10/Automated_Research_Paper_Reviewer/issues)
- **Discussions:** [Q&A Forum](https://github.com/Likhithmessi10/Automated_Research_Paper_Reviewer/discussions)

For questions or collaboration opportunities, please open an issue on GitHub.

---

## �‍💻 Developed By

**Team:** Automated Research Paper Reviewer  
**Stream:** CSE (AI & ML)  
**Project:** Final Year Major Project (2025)  
**Repository:** [GitHub](https://github.com/Likhithmessi10/Automated_Research_Paper_Reviewer)

---

## �📜 License

This project is intended for educational and research purposes. Please cite appropriately if used in academic work:

```bibtex
@software{automated_research_reviewer,
  title={Automated Research Paper Reviewer},
  author={PaperLens Team},
  year={2025},
  url={https://github.com/Likhithmessi10/Automated_Research_Paper_Reviewer}
}
```
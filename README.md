
# 📝 Automated Research Paper Reviewer

An AI-powered system that automatically reviews research papers (PDF format) using NLP and plagiarism detection. Provides:
- ✅ Strength detection
- ❌ Weakness identification
- 💡 Improvement suggestions
- 📊 Plagiarism & originality checking
- 🤖 AI-powered text rewriting with Ollama
- 📈 Confidence-based verdict (Accept / Weak Accept / Reject)

This project is built as a **Final Year CSE (AI/ML) Project** and is suitable for:
- Academic paper review automation
- Research paper quality assessment
- AI-based document evaluation systems
- Academic integrity checking  

---

## 🚀 Features

- Upload research paper in **PDF format**
- Automatic **section detection** (Abstract, Introduction, Methodology, Results, Conclusion)
- Sentence-level **NLP-based analysis** using spaCy
- Heuristic-based **Strength, Weakness & Improvement extraction**
- **Online plagiarism detection** with originality scoring
- **AI-powered text rewriting** using local Ollama (LLaMA 3.1)
- **Final score + confidence-based verdict**
- Interactive **dashboard with charts and metrics**
- Downloadable **TXT report & CSV data**
- **REST API endpoint** for integration with mobile/web apps
- Clean modern **Streamlit UI** for interactive analysis

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit  
- **Backend API:** FastAPI + Uvicorn
- **NLP:** spaCy (en_core_web_sm)  
- **PDF Processing:** PyMuPDF (fitz)  
- **Visualization:** Plotly  
- **Data Handling:** Pandas  
- **AI Rewriting:** Ollama (LLaMA 3.1:8b)
- **Plagiarism Detection:** Google Search API & custom heuristics  

---

## 📁 Project Structure

```
Automated_Research_paper_reviewer/
│
├── api.py                     # FastAPI REST endpoint
├── frontend.py                # Streamlit interactive UI
├── review_model.py            # Core AI & NLP logic with Ollama rewriting
├── online_plagiarism.py       # Plagiarism detection module
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
└── __pycache__/               # Python cache files
```

---

## ✅ Installation & Setup

### 1️⃣ Clone the Repository
git clone https://github.com/your-username/paperlens.git  
cd paperlens

---

### 2️⃣ Create Virtual Environment (Optional)
python -m venv venv

Activate:
- Windows: venv\Scripts\activate  
- Mac/Linux: source venv/bin/activate

---

### 3️⃣ Install Dependencies
pip install -r requirements.txt

---

### 4️⃣ Download spaCy Model
python -m spacy download en_core_web_sm

---

### 5️⃣ Start Ollama Service (Optional - for AI rewriting)
```bash
ollama serve
```
In another terminal, pull the required model:
```bash
ollama pull llama3.1:8b
```

### 6️⃣ Run the Application

**Option A: Streamlit Frontend (Interactive UI)**
```bash
streamlit run frontend.py
```
Access at: `http://localhost:8501`

**Option B: FastAPI REST Backend (for mobile/web apps)**
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```
Access at: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

---

## 🌐 Deployment

This project can be deployed on:
- ✅ Streamlit Cloud
- ✅ Render
- ✅ Railway

---

## 📊 Output Includes

- **Final Verdict:** Accept / Weak Accept / Reject  
- **Confidence Score:** 0.0-1.0 normalized score
- **Strengths List:** Auto-detected paper strengths
- **Weaknesses List:** Identified issues and limitations
- **Improvement Suggestions:** Recommended enhancements
- **Plagiarism Report:** Plagiarism %, Originality %, Risk Level
- **Rewritten Texts:** AI-enhanced academic versions (via Ollama)
- **Downloadable Report:** TXT format with full analysis
- **CSV Dataset:** Structured data export

## 🔌 API Endpoints

### POST `/analyze`
Submit a research paper for analysis.

**Request:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@paper.pdf" \
  -F "rewrite=true"
```

**Response:**
```json
{
  "report": "📝 AUTOMATED RESEARCH PAPER REVIEW REPORT\n..."
}
```

**Parameters:**
- `file` (File): PDF paper file to analyze
- `rewrite` (bool): Enable AI rewriting with Ollama (default: true)

## ⚙️ Configuration

### Ollama Integration
- Requires local Ollama service running on `http://localhost:11434`
- Default model: `llama3.1:8b`
- Can be customized in `api.py` and `review_model.py`

### NLP Model
- spaCy model: `en_core_web_sm`
- Automatically loaded in `review_model.py`

## 🚨 System Requirements

- Python 3.8+
- Local Ollama service (optional, for AI text rewriting)
- PDF file for analysis
- Internet connection (for plagiarism checks)

---

## 🔮 Future Enhancements

- ⚡ Multi-language Support  
- 🎯 Journal-specific Scoring Models  
- 🔐 Enhanced Security & Privacy Features  
- 📱 Mobile App Integration  
- ☁️ Cloud Deployment Optimization  

---

## 👨‍💻 Developed By

Team Name: PaperLens  
Branch: CSE (AI & ML)  
Project Type: Final Year Major Project  
Year: 2025  

---

## 📜 License

This project is for educational and research purposes only.

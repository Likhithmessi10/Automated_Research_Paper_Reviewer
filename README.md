
# 📝 PaperLens – AI Research Paper Reviewer

PaperLens is an AI-powered web application that automatically reviews research papers (PDF format) and provides:
- ✅ Strength detection
- ❌ Weakness identification
- 💡 Improvement suggestions
- 📊 Confidence-based verdict (Accept / Weak Accept / Reject)

This project is built as a **Final Year CSE (AI/ML) Project** and is suitable for:
- Academic demonstrations  
- Research paper analysis  
- AI-based document evaluation systems  

---

## 🚀 Features

- Upload research paper in **PDF format**
- Automatic **section detection**
- Sentence-level **NLP-based analysis**
- Heuristic-based **Strength, Weakness & Improvement extraction**
- **Final score + confidence-based verdict**
- Interactive **dashboard with charts**
- Downloadable **TXT report & CSV data**
- Clean modern **Streamlit UI**

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit  
- **Backend Logic:** Python  
- **NLP:** spaCy  
- **PDF Processing:** PyMuPDF  
- **Visualization:** Plotly  
- **Data Handling:** Pandas  

---

## 📁 Project Structure

paperlens/
│
├── frontend.py          # Streamlit frontend
├── review_model.py     # Core AI & NLP logic
├── requirements.txt    # Dependencies
├── README.md           # Project documentation
└── .gitignore          # Ignored files

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

### 5️⃣ Run the Application
streamlit run frontend.py

---

## 🌐 Deployment

This project can be deployed on:
- ✅ Streamlit Cloud
- ✅ Render
- ✅ Railway

---

## 📊 Output Includes

- Final Verdict: Accept / Weak Accept / Reject  
- Confidence Score  
- Strengths List  
- Weaknesses List  
- Improvement Suggestions  
- Downloadable Text Report  
- Downloadable CSV Dataset  

---

## 🔮 Future Enhancements

- ✅ Plagiarism Detection  
- ✅ Deep Learning-based Review System  
- ✅ Journal-grade Paper Scoring  
- ✅ Multi-language Support  

---

## 👨‍💻 Developed By

Team Name: PaperLens  
Branch: CSE (AI & ML)  
Project Type: Final Year Major Project  
Year: 2025  

---

## 📜 License

This project is for educational and research purposes only.

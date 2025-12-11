# 📄 User Need & Requirement Mapping: PaperLens

**Project Name:** PaperLens (AI Research Paper Reviewer)  
**Track:** App Ventures (Mobile & Web)  
**Team:** PaperLens  

---

## 1. 🎭 User Personas (Who are we solving for?)

We identified **three key user personas** who struggle with the current academic review process.

### **Persona A: The Anxious Student (Riya)**
* **Role:** Final Year CS Undergrad.
* **Pain Point:** She has written her first research paper but is terrified of rejection. She doesn't know if her methodology is sound or if her English is professional enough.
* **Needs:** Instant feedback, confidence scoring, and help rewriting informal sentences.
* **Quote:** *"I just want to know if my paper is good enough before I submit it to the professor."*

### **Persona B: The Overworked Professor (Dr. Aravind)**
* **Role:** Senior Professor & Conference Reviewer.
* **Pain Point:** He receives 50+ papers to review in a week. Reading every word is impossible. He needs a quick way to filter out low-quality submissions.
* **Needs:** A summary of the methodology, a quick plagiarism check, and a structured scorecard (NeurIPS style) to make fast decisions.
* **Quote:** *"I need a tool that highlights the flaws immediately so I don't waste time on bad papers."*

### **Persona C: The PhD Researcher (Vikram)**
* **Role:** Research Scholar.
* **Pain Point:** He is worried about accidentally plagiarizing or missing a baseline comparison in his experiments.
* **Needs:** Deep section analysis to catch logical gaps and a rigorous plagiarism risk assessment.

---

## 2. 🧠 User Need vs. Feature Mapping

We brainstormed features directly addressing the needs of Riya, Dr. Aravind, and Vikram.

| User Need (The Problem) | Proposed Feature (The Solution) | Implementation (Tech) |
| :--- | :--- | :--- |
| **"Is my paper good?"** | **Confidence Score & Verdict** | Heuristic scoring + AI Verdict (Accept/Reject). |
| **"Fix my bad English."** | **AI Academic Rewriter** | Llama 3 (Ollama) rewrites informal text to professional tone. |
| **"Did I copy anything?"** | **Plagiarism Risk Meter** | Online search integration to check sentence originality. |
| **"Is my logic sound?"** | **Deep Section Analysis** | LLM reads "Methodology" & "Results" to find semantic flaws. |
| **"Quick overview."** | **Expert Scorecard (v2)** | Quantitative 1-10 scores on Originality, Clarity, & Significance. |
| **"Access anywhere."** | **Mobile App Interface** | Flutter App + FastAPI Backend for on-the-go reviews. |

---

## 3. 🚀 Feature List (Deliverables)

Based on the brainstorming above, here is the final feature set for **PaperLens v2**:

### **Core Features (MVP)**
1.  **PDF Parsing Engine:** Automatically extracts abstract, intro, and methodology sections.
2.  **Heuristic Analysis:** Instantly spots "weak words" (e.g., "small dataset", "limited results").
3.  **NeurIPS-Style Scorecard:** Generates a professional 1-10 rating for Originality and Methodology.
4.  **AI Rewriting Tool:** Side-by-side comparison of "Original" vs. "Polished" text.
5.  **Plagiarism Detector:** Real-time check against online sources.

### **UX Enhancements**
* **Visual Dashboard:** Uses color-coded gauges (Green/Red) for instant "Accept/Reject" feedback.
* **One-Click Report:** Downloadable detailed TXT report for record-keeping.
* **Mobile Experience:** Simple "Upload & Scan" workflow for students.
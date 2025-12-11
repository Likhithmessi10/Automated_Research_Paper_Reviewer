import fitz  # PyMuPDF
import re
import spacy
import requests
import json
from typing import List, Tuple

# local plagiarism integration (your file)
from online_plagiarism import check_plagiarism_smallseotools

# -----------------------
# Load spaCy model once
# -----------------------
nlp = spacy.load("en_core_web_sm")

# ==========================================
# 🟢 v1 FEATURES: Pattern Matching & Basic Scoring
# ==========================================

STRENGTH_PATTERNS = [
    "outperforms", "significant improvement", "robust", "effective",
    "state-of-the-art", "novel approach", "high accuracy",
    "consistent performance", "experimentally validated",
    "strong results", "superior performance"
]

WEAKNESS_PATTERNS = [
    "small dataset", "limited dataset", "lacks validation",
    "not compared", "no comparison", "unclear",
    "insufficient", "poor performance", "overfitting",
    "lack of generalization", "limited scope",
    "not statistically significant"
]

IMPROVEMENT_PATTERNS = [
    "future work", "can be improved", "should consider",
    "can be extended", "requires further study",
    "needs improvement", "can be optimized",
    "future extension", "should be explored"
]

# -----------------------
# PDF → Text
# -----------------------
def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text

# -----------------------
# Section Detection
# -----------------------
def detect_sections(text: str) -> dict:
    sections = {
        "abstract": "", "introduction": "", "methodology": "",
        "results": "", "conclusion": ""
    }

    clean_text = text.lower()

    patterns = {
        "abstract": r"abstract(.*?)(introduction|1\.)",
        "introduction": r"(introduction|1\.)(.*?)(methodology|methods|2\.)",
        "methodology": r"(methodology|methods|2\.)(.*?)(results|3\.)",
        "results": r"(results|3\.)(.*?)(conclusion|4\.)",
        "conclusion": r"(conclusion|4\.)(.*)"
    }

    for section, pattern in patterns.items():
        match = re.search(pattern, clean_text, re.DOTALL)
        if match:
            sections[section] = match.group(0).strip()

    return sections

# -----------------------
# Sentence Preprocessing
# -----------------------
def preprocess_and_tokenize(section_text: str) -> List[str]:
    if not section_text:
        return []

    doc = nlp(section_text)
    sentences = []

    for sent in doc.sents:
        clean_sent = sent.text.strip()
        if len(clean_sent) > 15:
            sentences.append(clean_sent)

    return sentences

# -----------------------
# Sentence Classification
# -----------------------
def classify_sentences(sentences: List[str]) -> Tuple[List[str], List[str], List[str]]:
    strengths, weaknesses, improvements = [],[],[]
    
    for sent in sentences:
        sent_lower = sent.lower()
        if any(pat in sent_lower for pat in STRENGTH_PATTERNS):
            strengths.append(sent)
        elif any(pat in sent_lower for pat in WEAKNESS_PATTERNS):
            weaknesses.append(sent)
        elif any(pat in sent_lower for pat in IMPROVEMENT_PATTERNS):
            improvements.append(sent)

    return strengths, weaknesses, improvements

# -----------------------
# v1 Scoring
# -----------------------
WEIGHTS = {"strength": 1.0, "weakness": -1.2, "improvement": -0.5}

def compute_final_score(strengths: List[str], weaknesses: List[str], improvements: List[str]) -> Tuple[float, float]:
    score = 0.0
    score += WEIGHTS["strength"] * len(strengths)
    score += WEIGHTS["weakness"] * len(weaknesses)
    score += WEIGHTS["improvement"] * len(improvements)

    # Normalize to 0..1 for confidence
    max_possible = 10.0
    normalized_score = max(0.0, min(1.0, (score + max_possible) / (2.0 * max_possible)))

    return score, normalized_score

def generate_verdict(confidence_score: float) -> str:
    if confidence_score > 0.65: return "ACCEPT"
    elif confidence_score > 0.45: return "WEAK ACCEPT"
    else: return "REJECT"

# ==========================================
# 🔵 v2 FEATURES: Deep LLM Analysis & Scorecards
# ==========================================

SYSTEM_PROMPT = """
You are a Senior Area Chair for a top-tier AI conference (NeurIPS/ICML).
Your job is to critically evaluate this research paper.
Be strict, fair, and constructive.
You must output your response in valid JSON format only.
"""

def analyze_section_with_llm(section_name: str, section_text: str, model: str):
    """
    Asks Ollama to score and critique a specific section.
    """
    if not section_text or len(section_text) < 50:
        return None

    user_prompt = f"""
    Analyze the following '{section_name}' section of a research paper.
    
    Task:
    1. Summarize the main point in 1 sentence.
    2. Identify 2 specific weaknesses (logic gaps, missing definitions, weak baselines).
    3. Rate 'Section Quality' (1-10) based on clarity and rigor.

    Input Text:
    "{section_text[:3500]}"  # Truncated to avoid token limits

    Output Format (JSON ONLY):
    {{
        "summary": "The authors propose...",
        "weaknesses": ["Weakness 1...", "Weakness 2..."],
        "score": 8
    }}
    """
    
    payload = {
        "model": model,
        "system": SYSTEM_PROMPT,
        "prompt": user_prompt,
        "stream": False,
        "format": "json",        # FORCE JSON output
        "temperature": 0.2
    }
    
    try:
        # Increased timeout for deep analysis
        resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
        data = resp.json()
        return json.loads(data["response"])
    except Exception as e:
        print(f"❌ AI Analysis failed for {section_name}: {e}")
        return None

def generate_overall_critique(paper_summary_text: str, model: str):
    """
    Generates the final 'NeurIPS-style' scorecard.
    """
    user_prompt = f"""
    Based on the abstract and conclusion below, generate a final review scorecard.
    
    Text: "{paper_summary_text[:3000]}"
    
    Task:
    1. Score 'Originality', 'Methodology', 'Clarity', 'Significance' (1-10).
    2. Provide a Final Recommendation (Accept, Weak Accept, Reject).
    3. Write a 1-sentence final verdict reason.

    Output Format (JSON ONLY):
    {{
        "originality": 8,
        "methodology": 7,
        "clarity": 9,
        "significance": 6,
        "recommendation": "Weak Accept",
        "reason": "The idea is novel but experiments are weak."
    }}
    """
    payload = {
        "model": model, "system": SYSTEM_PROMPT,
        "prompt": user_prompt, "stream": False,
        "format": "json", "temperature": 0.2
    }
    try:
        resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
        data = resp.json()
        return json.loads(data["response"])
    except:
        return {}

# -----------------------
# Helper: Strict Rewriting (v1 Fixed)
# -----------------------
def rewrite_with_ollama(text: str, model: str = "llama3.1:8b", timeout: int = 60) -> str:
    """
    Sends a single rewrite job to local Ollama and returns the rewritten text.
    """
    try:
        prompt = (
            "You are a strict academic editor. Rewrite the specific input sentence below into "
            "concise, objective, and professional academic English.\n\n"
            "STRICT RULES:\n"
            "1. Output ONLY the rewritten sentence.\n"
            "2. Do NOT use conversational fillers.\n"
            "3. Avoid first-person pronouns (like 'we', 'our').\n"
            f"Input: \"{text}\"\n\nOutput:"
        )
        
        payload = {
            "model": model, "prompt": prompt, "stream": False,
            "max_tokens": 256, "temperature": 0.1, "stop": ["Input:", "\n\n"]
        }

        resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=timeout)
        if resp.status_code != 200: return text

        out = resp.json().get("response", "").strip()
        if out.startswith('"') and out.endswith('"'): out = out[1:-1]
        if ":" in out[:20]: out = out.split(":", 1)[1].strip()
        
        return out if out else text

    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return text

def rewrite_texts_with_ollama(texts: List[str], model: str = "llama3.1:8b") -> List[str]:
    return [rewrite_with_ollama(t, model=model) for t in texts]


# -----------------------
# Report Formatter (Combines v1 and v2)
# -----------------------
def generate_final_report(strengths, weaknesses, improvements, verdict, confidence, v2_card=None):
    report = "\n" + "=" * 60 + "\n"
    report += "📝 AUTOMATED RESEARCH PAPER REVIEW REPORT\n"
    report += "=" * 60 + "\n\n"

    # v2 Highlights (if available)
    if v2_card:
        report += "🏆 EXPERT REVIEW SCORECARD (AI)\n"
        report += f"• Originality: {v2_card.get('originality', '-')}/10\n"
        report += f"• Methodology: {v2_card.get('methodology', '-')}/10\n"
        report += f"• Recommendation: {v2_card.get('recommendation', 'N/A')}\n"
        report += f"• Verdict Reason: {v2_card.get('reason', '')}\n\n"
        report += "-" * 60 + "\n\n"

    # v1 Details
    report += "✅ STRENGTHS (Heuristic):\n"
    if strengths:
        for idx, s in enumerate(strengths[:5], 1):
            report += f"{idx}. {s}\n"
    else:
        report += "No significant strengths detected.\n"

    report += "\n❌ WEAKNESSES (Heuristic):\n"
    if weaknesses:
        for idx, w in enumerate(weaknesses[:5], 1):
            report += f"{idx}. {w}\n"
    else:
        report += "No major weaknesses detected.\n"

    report += "\n" + "-" * 60 + "\n"
    report += f"🧠 FINAL VERDICT (Heuristic): {verdict}\n"
    report += "-" * 60 + "\n"

    return report


# ==========================================
# 🚀 MAIN PIPELINE ENTRYPOINT
# ==========================================
def review_pdf(pdf_path: str, rewrite: bool = True, ollama_model: str = "llama3.1:8b") -> dict:
    """
    Main function. Runs v1 Heuristics AND v2 LLM Analysis.
    """
    
    # 1. Extract text & Sections
    text = extract_text_from_pdf(pdf_path)
    sections = detect_sections(text)

    # --- PHASE 1: v1 Heuristics (Fast) ---
    abstract_sents = preprocess_and_tokenize(sections.get("abstract", ""))
    intro_sents = preprocess_and_tokenize(sections.get("introduction", ""))
    method_sents = preprocess_and_tokenize(sections.get("methodology", ""))
    result_sents = preprocess_and_tokenize(sections.get("results", ""))
    conclusion_sents = preprocess_and_tokenize(sections.get("conclusion", ""))

    all_strengths, all_weaknesses, all_improvements = [], [], []
    for section in [abstract_sents, intro_sents, method_sents, result_sents, conclusion_sents]:
        s, w, i = classify_sentences(section)
        all_strengths.extend(s)
        all_weaknesses.extend(w)
        all_improvements.extend(i)

    # v1 Scoring
    final_score, confidence = compute_final_score(all_strengths, all_weaknesses, all_improvements)
    verdict = generate_verdict(confidence)

    # Plagiarism Check
    try:
        plagiarism_percent, originality_percent, plagiarism_risk = check_plagiarism_smallseotools(text)
        try: plagiarism_percent = int(plagiarism_percent)
        except: plagiarism_percent = 0
        try: originality_percent = int(originality_percent)
        except: originality_percent = max(0, 100 - plagiarism_percent)
    except:
        plagiarism_percent, originality_percent, plagiarism_risk = 0, 100, "UNAVAILABLE"

    if isinstance(plagiarism_percent, (int, float)) and plagiarism_percent > 40:
        verdict = "❌ REJECT (PLAGIARISM)"

    # --- PHASE 2: v2 Deep AI Analysis (The "Brain") ---
    # We analyze key sections independently
    print("🤖 Running Expert AI Analysis on Sections...")
    
    method_review = analyze_section_with_llm("Methodology", sections.get("methodology", ""), ollama_model)
    results_review = analyze_section_with_llm("Results", sections.get("results", ""), ollama_model)
    
    # Generate Overall Scorecard using Abstract + Conclusion
    summary_text = (sections.get("abstract", "") + "\n" + sections.get("conclusion", ""))
    final_card = generate_overall_critique(summary_text, ollama_model)
    if method_review and "score" in method_review:
        final_card["methodology"] = method_review["score"]

    if results_review and "score" in results_review:
        # We can also add a 'Results' field to the card if you want
        final_card["results_score"] = results_review["score"]
    # --- PHASE 3: Rewriting (Optional) ---
    rewritten_strengths = []
    rewritten_weaknesses = []
    rewritten_improvements = []
    
    if rewrite:
        # We limit to top 3 to save time
        if all_strengths:
            rewritten_strengths = rewrite_texts_with_ollama(all_strengths[:3], model=ollama_model)
        if all_weaknesses:
            rewritten_weaknesses = rewrite_texts_with_ollama(all_weaknesses[:3], model=ollama_model)
        if all_improvements:
            rewritten_improvements = rewrite_texts_with_ollama(all_improvements[:3], model=ollama_model)

    # Generate Report
    report = generate_final_report(
        rewritten_strengths if rewrite else all_strengths,
        rewritten_weaknesses if rewrite else all_weaknesses,
        all_improvements, # We usually don't rewrite improvements to save time, but you can add it
        verdict,
        confidence,
        v2_card=final_card
    )

    return {
        # v1 Data
        "strengths": all_strengths,
        "weaknesses": all_weaknesses,
        "improvements": all_improvements,
        "rewritten_strengths": rewritten_strengths,
        "rewritten_weaknesses": rewritten_weaknesses,
        "rewritten_improvements": rewritten_improvements,
        "final_score": final_score,
        "confidence": confidence,
        "verdict": verdict,
        "plagiarism_percent": plagiarism_percent,
        "originality_percent": originality_percent,
        "plagiarism_risk": plagiarism_risk,
        "report": report,
        
        # v2 Data (New!)
        "methodology_review": method_review,
        "results_review": results_review,
        "final_card": final_card
    }

if __name__ == "__main__":
    # Local Test
    res = review_pdf("sample.pdf", rewrite=False)
    print(res["report"])
    print("\n--- v2 JSON Data ---")
    print(json.dumps(res["final_card"], indent=2))
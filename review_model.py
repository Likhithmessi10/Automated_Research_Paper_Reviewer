# review_model.py
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
        "abstract": "",
        "introduction": "",
        "methodology": "",
        "results": "",
        "conclusion": ""
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
# Heuristic Patterns
# -----------------------
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
# Sentence Classification
# -----------------------
def classify_sentences(sentences: List[str]) -> Tuple[List[str], List[str], List[str]]:
    strengths = []
    weaknesses = []
    improvements = []

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
# Scoring + Verdict
# -----------------------
WEIGHTS = {
    "strength": 1.0,
    "weakness": -1.2,
    "improvement": -0.5
}


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
    if confidence_score > 0.65:
        return "ACCEPT"
    elif confidence_score > 0.45:
        return "WEAK ACCEPT"
    else:
        return "REJECT"


# -----------------------
# Ollama Rewriting Helpers
# -----------------------
def rewrite_with_ollama(text: str, model: str = "llama3.1:8b", timeout: int = 30) -> str:
    """
    Sends a single rewrite job to local Ollama and returns the rewritten text.
    If Ollama fails, returns the original text.
    """
    try:
        prompt = (
            "You are an academic writing assistant. Rewrite the following reviewer-style sentence "
            "into clear, concise, and original academic English suitable for a peer-review comment. "
            "Keep meaning but avoid copying exact wording.\n\n"
            f"Input: {text}\n\n"
            "Rewritten:"
        )
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": 256,
            "temperature": 0.15,
            "top_p": 0.95,
            "stop": None
        }

        resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=timeout)
        if resp.status_code != 200:
            return text

        data = resp.json()

        # Ollama's API format may vary; try common fields
        # Preferred: data.get("output") or data.get("response") or data.get("generated_text")
        out = ""
        if isinstance(data, dict):
            # common keys
            if "response" in data and isinstance(data["response"], str):
                out = data["response"]
            elif "output" in data:
                if isinstance(data["output"], str):
                    out = data["output"]
                elif isinstance(data["output"], list) and data["output"]:
                    out = data["output"][0].get("content", "") if isinstance(data["output"][0], dict) else str(data["output"][0])
            elif "generated_text" in data:
                out = data["generated_text"]
            elif "completion" in data:
                out = data["completion"]
            else:
                # Fallback: try to stringify the whole JSON
                out = json.dumps(data)
        else:
            out = str(data)

        out = out.strip()
        if not out:
            return text

        return out

    except Exception:
        # On any failure, return original text to avoid crashing pipeline
        return text


def rewrite_texts_with_ollama(texts: List[str], model: str = "llama3.1:8b") -> List[str]:
    """
    Rewrite a list of short texts using Ollama, sequentially.
    Keeps original text if rewriting fails.
    """
    rewritten = []
    for t in texts:
        # keep prompts short — Ollama handles small inputs quickly
        rewritten_text = rewrite_with_ollama(t, model=model)
        rewritten.append(rewritten_text)
    return rewritten


# -----------------------
# Final Report Formatter
# -----------------------
def generate_final_report(strengths, weaknesses, improvements, verdict, confidence):
    report = "\n" + "=" * 60 + "\n"
    report += "📝 AUTOMATED RESEARCH PAPER REVIEW REPORT\n"
    report += "=" * 60 + "\n\n"

    report += "✅ STRENGTHS:\n"
    if strengths:
        for idx, s in enumerate(strengths[:5], 1):
            report += f"{idx}. {s}\n"
    else:
        report += "No significant strengths detected.\n"

    report += "\n❌ WEAKNESSES:\n"
    if weaknesses:
        for idx, w in enumerate(weaknesses[:5], 1):
            report += f"{idx}. {w}\n"
    else:
        report += "No major weaknesses detected.\n"

    report += "\n🛠 SUGGESTED IMPROVEMENTS:\n"
    if improvements:
        for idx, i in enumerate(improvements[:5], 1):
            report += f"{idx}. {i}\n"
    else:
        report += "No major improvements suggested.\n"

    report += "\n" + "-" * 60 + "\n"
    report += f"🧠 FINAL VERDICT: {verdict}\n"
    report += f"📊 CONFIDENCE SCORE: {round(confidence, 2)}\n"
    report += "-" * 60 + "\n"

    return report


# -----------------------
# MAIN ENTRYPOINT
# -----------------------
def review_pdf(pdf_path: str, rewrite: bool = True, ollama_model: str = "llama3.1:8b") -> dict:
    """
    Main function to call from backend or frontend.
    Parameters:
        - pdf_path: path to PDF file
        - rewrite: whether to run Ollama rewriting on extracted items
        - ollama_model: model name available in local Ollama
    Returns:
        dict with analysis results and rewritten texts (if rewrite=True)
    """

    # 1. Extract text
    text = extract_text_from_pdf(pdf_path)

    # 2. Detect sections
    sections = detect_sections(text)

    # 3. Tokenize sentences from each section
    abstract_sents = preprocess_and_tokenize(sections.get("abstract", ""))
    intro_sents = preprocess_and_tokenize(sections.get("introduction", ""))
    method_sents = preprocess_and_tokenize(sections.get("methodology", ""))
    result_sents = preprocess_and_tokenize(sections.get("results", ""))
    conclusion_sents = preprocess_and_tokenize(sections.get("conclusion", ""))

    # 4. Classify sentences
    all_strengths, all_weaknesses, all_improvements = [], [], []
    for section in [abstract_sents, intro_sents, method_sents, result_sents, conclusion_sents]:
        s, w, i = classify_sentences(section)
        all_strengths.extend(s)
        all_weaknesses.extend(w)
        all_improvements.extend(i)

    # 5. Compute score + verdict (initial)
    final_score, confidence = compute_final_score(
        all_strengths, all_weaknesses, all_improvements
    )
    verdict = generate_verdict(confidence)

    # 6. Online plagiarism check (may be slow/unreliable depending on free service)
    try:
        plagiarism_percent, originality_percent, plagiarism_risk = check_plagiarism_smallseotools(text)
        # ensure integer percentages and risk are normalized
        try:
            plagiarism_percent = int(plagiarism_percent)
        except Exception:
            plagiarism_percent = 0
        try:
            originality_percent = int(originality_percent)
        except Exception:
            originality_percent = max(0, 100 - plagiarism_percent)
        if not isinstance(plagiarism_risk, str):
            plagiarism_risk = str(plagiarism_risk).upper()
    except Exception:
        plagiarism_percent, originality_percent, plagiarism_risk = 0, 100, "UNAVAILABLE"

    # 7. Auto-reject on high plagiarism
    if isinstance(plagiarism_percent, (int, float)) and plagiarism_percent > 40:
        verdict = "❌ REJECT (PLAGIARISM)"

    # 8. Optionally rewrite extracted items via Ollama
    rewritten_strengths = []
    rewritten_weaknesses = []
    rewritten_improvements = []
    if rewrite:
        try:
            rewritten_strengths = rewrite_texts_with_ollama(all_strengths, model=ollama_model) if all_strengths else []
            rewritten_weaknesses = rewrite_texts_with_ollama(all_weaknesses, model=ollama_model) if all_weaknesses else []
            rewritten_improvements = rewrite_texts_with_ollama(all_improvements, model=ollama_model) if all_improvements else []
        except Exception:
            # if Ollama fails for any reason, fallback to originals
            rewritten_strengths = all_strengths
            rewritten_weaknesses = all_weaknesses
            rewritten_improvements = all_improvements
    else:
        # keep originals if rewrite disabled
        rewritten_strengths = all_strengths
        rewritten_weaknesses = all_weaknesses
        rewritten_improvements = all_improvements

    # 9. Build human-readable report AFTER plagiarism and rewrite
    report = generate_final_report(
        rewritten_strengths,
        rewritten_weaknesses,
        rewritten_improvements,
        verdict,
        confidence,
    )

    return {
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
    }


# Simple local test
if __name__ == "__main__":
    result = review_pdf("sample_paper.pdf", rewrite=False)
    print(result["report"])

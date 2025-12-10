import fitz  # PyMuPDF
import re
import spacy

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
def preprocess_and_tokenize(section_text: str):
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
def classify_sentences(sentences):
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

def compute_final_score(strengths, weaknesses, improvements):
    score = 0
    score += WEIGHTS["strength"] * len(strengths)
    score += WEIGHTS["weakness"] * len(weaknesses)
    score += WEIGHTS["improvement"] * len(improvements)

    max_possible = 10
    normalized_score = max(0, min(1, (score + max_possible) / (2 * max_possible)))

    return score, normalized_score


def generate_verdict(confidence_score: float) -> str:
    if confidence_score > 0.65:
        return "ACCEPT"
    elif confidence_score > 0.45:
        return "WEAK ACCEPT"
    else:
        return "REJECT"


# -----------------------
# Final Report Formatter
# -----------------------
def generate_final_report(strengths, weaknesses, improvements, verdict, confidence):
    report = "\n" + "="*60 + "\n"
    report += "📝 AUTOMATED RESEARCH PAPER REVIEW REPORT\n"
    report += "="*60 + "\n\n"

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

    report += "\n" + "-"*60 + "\n"
    report += f"🧠 FINAL VERDICT: {verdict}\n"
    report += f"📊 CONFIDENCE SCORE: {round(confidence, 2)}\n"
    report += "-"*60 + "\n"

    return report


# -----------------------
# MAIN ENTRYPOINT
# -----------------------
def review_pdf(pdf_path: str) -> dict:
    """
    Main function to call from backend.
    Returns a dictionary with all review details.
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

    all_strengths, all_weaknesses, all_improvements = [], [], []

    for section in [abstract_sents, intro_sents, method_sents, result_sents, conclusion_sents]:
        s, w, i = classify_sentences(section)
        all_strengths.extend(s)
        all_weaknesses.extend(w)
        all_improvements.extend(i)

    # 4. Compute score + verdict
    final_score, confidence = compute_final_score(
        all_strengths, all_weaknesses, all_improvements
    )
    verdict = generate_verdict(confidence)

    # 5. Build human-readable report
    report = generate_final_report(
        all_strengths,
        all_weaknesses,
        all_improvements,
        verdict,
        confidence,
    )

    return {
        "strengths": all_strengths,
        "weaknesses": all_weaknesses,
        "improvements": all_improvements,
        "final_score": final_score,
        "confidence": confidence,
        "verdict": verdict,
        "report": report,
    }


# Simple local test
if __name__ == "__main__":
    result = review_pdf("sample_paper.pdf")
    print(result["report"])

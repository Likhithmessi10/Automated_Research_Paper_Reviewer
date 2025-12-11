from fastapi import FastAPI, File, UploadFile, Form
import tempfile, os, traceback, time
import requests
from typing import Any

# adjust imports to your project layout
from review_model import review_pdf, generate_final_report
from online_plagiarism import check_plagiarism_smallseotools

app = FastAPI()


# ---------- helper: safe call to Ollama ----------
def rewrite_with_ollama(text: str):
    try:
        payload = {
            "model": "llama3.1:8b",
            "prompt": (
                "Rewrite the following text professionally in a third-person academic tone. "
                "Return ONLY the rewritten sentence. Do NOT add any explanation or introduction.\n\n"
                f"TEXT:\n{text}\n\nREWRITE:"
            ),
            "stream": False
        }

        r = requests.post("http://localhost:11434/api/generate", json=payload)
        j = r.json()

        output = j.get("response") or text

        # Remove any leftover bullshit like "Here is the rewritten text:"
        remove_phrases = [
            "Here is the rewritten text:",
            "Here is the rewritten text in a professional, third-person academic tone:",
            "Here is the rewritten text in a third-person academic tone:",
            "Rewritten:",
            "REWRITE:"
        ]

        for p in remove_phrases:
            output = output.replace(p, "")

        return output.strip()

    except Exception:
        return text

# ---------- helper: safe generate_final_report caller ----------
def safe_generate_final_report(strengths, weaknesses, improvements, verdict: str, confidence: float) -> str:
    """
    Try multiple signatures for generate_final_report:
     - preferred: generate_final_report(strengths, weaknesses, improvements, verdict, confidence)
     - fallback: generate_final_report(strengths, weaknesses, improvements)
     - fallback: join lists manually
    """
    try:
        return generate_final_report(strengths, weaknesses, improvements, verdict, confidence)
    except TypeError:
        # try 3-arg
        try:
            return generate_final_report(strengths, weaknesses, improvements)
        except Exception:
            pass
    except Exception:
        pass

    # final fallback: build a simple text summary
    parts = []
    if strengths:
        parts.append("Strengths:\n" + "\n".join([("- " + s) for s in strengths]))
    if weaknesses:
        parts.append("Weaknesses:\n" + "\n".join([("- " + w) for w in weaknesses]))
    if improvements:
        parts.append("Improvements:\n" + "\n".join([("- " + i) for i in improvements]))
    parts.append(f"Verdict: {verdict}, Confidence: {confidence}")
    return "\n\n".join(parts)


# ---------- main /analyze ----------
@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...), rewrite: str = Form("true")) -> Any:
    """
    Returns JSON expected by Flutter. Defensive and logs errors gracefully.
    """
    start_ts = time.time()
    tmp_folder = None
    try:
        tmp_folder = tempfile.mkdtemp()
        file_path = os.path.join(tmp_folder, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # call review model
        rv = review_pdf(file_path)

        # Normalize rv to dict
        if isinstance(rv, dict):
            data = rv
        elif isinstance(rv, (list, tuple)):
            # attempt to map common tuple shapes -> convert into dict
            # if it's already (extracted, strengths, weaknesses, improvements, final_card)
            data = {}
            try:
                if len(rv) >= 4:
                    # heuristic mapping
                    data["strengths"] = rv[1] if len(rv) > 1 else []
                    data["weaknesses"] = rv[2] if len(rv) > 2 else []
                    data["improvements"] = rv[3] if len(rv) > 3 else []
                    # final_card maybe present as 5th
                    if len(rv) > 4 and isinstance(rv[4], dict):
                        data["final_card"] = rv[4]
                        data["final_score"] = rv[4].get("final_score", 0.0)
                        data["verdict"] = rv[4].get("verdict", "UNKNOWN")
                        data["confidence"] = rv[4].get("confidence", 0.0)
                    else:
                        data["final_card"] = {}
                        data["final_score"] = 0.0
                        data["verdict"] = "UNKNOWN"
                        data["confidence"] = 0.0
                else:
                    # unknown shape -> return error to client
                    return {"error": "Unexpected tuple/list shape from review_pdf", "raw": str(rv)}
            except Exception as e:
                return {"error": "Failed to interpret tuple return from review_pdf", "trace": str(e), "raw": str(rv)}
        else:
            return {"error": "review_pdf returned unsupported type", "type": str(type(rv))}

        # Extract fields
        strengths = data.get("strengths", []) or []
        weaknesses = data.get("weaknesses", []) or []
        improvements = data.get("improvements", []) or []

        verdict = data.get("verdict", "UNKNOWN")
        confidence = float(data.get("confidence", 0.0) or 0.0)
        final_card = data.get("final_card", {})
        final_score = data.get("final_score", data.get("final_score", 0.0))

        # rewrite lists if requested
        if (rewrite or "true").lower() == "true":
            # be careful: large lists -> consider rate limit (we do them sequentially)
            rewritten_strengths = [rewrite_with_ollama(s) for s in strengths]
            rewritten_weaknesses = [rewrite_with_ollama(w) for w in weaknesses]
            rewritten_improvements = [rewrite_with_ollama(i) for i in improvements]
        else:
            rewritten_strengths = strengths
            rewritten_weaknesses = weaknesses
            rewritten_improvements = improvements

        # generate a final human-readable report using safe wrapper
        rewritten_text = safe_generate_final_report(
            rewritten_strengths, rewritten_weaknesses, rewritten_improvements, verdict, confidence
        )

        # optional plagiarism: use provided function on full text if present
        plag_percent = data.get("plagiarism_percent", None)
        plag_risk = data.get("plagiarism_risk", None)
        if plag_percent is None:
            try:
                full_text = data.get("full_text", "") or data.get("report", "") or ""
                p_p, p_orig, p_risk = check_plagiarism_smallseotools(full_text)
                if isinstance(p_p, int):
                    plag_percent = p_p
                if isinstance(p_risk, str):
                    plag_risk = p_risk
            except Exception:
                plag_percent = 0
                plag_risk = "UNAVAILABLE"

        duration = time.time() - start_ts

        return {
            "verdict": verdict,
            "final_card": final_card,
            "final_score": final_score,
            "confidence": confidence,

            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvements": improvements,

            "rewritten_strengths": rewritten_strengths,
            "rewritten_weaknesses": rewritten_weaknesses,
            "rewritten_improvements": rewritten_improvements,

            "rewritten_text": rewritten_text,

            "plagiarism_percent": plag_percent or 0,
            "plagiarism_risk": plag_risk or "UNAVAILABLE",

            "meta": {
                "runtime_seconds": round(duration, 2),
                "rewrote": (rewrite or "true").lower() == "true"
            }
        }

    except Exception as e:
        tb = traceback.format_exc()
        print("ERROR in /analyze:", tb)
        return {"error": str(e), "trace": tb}
    finally:
        # try cleanup
        try:
            if tmp_folder and os.path.isdir(tmp_folder):
                # remove file and folder
                for fname in os.listdir(tmp_folder):
                    try:
                        os.remove(os.path.join(tmp_folder, fname))
                    except Exception:
                        pass
                try:
                    os.rmdir(tmp_folder)
                except Exception:
                    pass
        except Exception:
            pass


# ---------- small /ask helper for manual testing ----------
from pydantic import BaseModel
class AskBody(BaseModel):
    prompt: str

@app.post("/ask")
def ask_model(body: AskBody):
    try:
        r = requests.post("http://localhost:11434/api/generate",
                          json={"model": "llama3.1:8b", "prompt": body.prompt, "stream": False},
                          timeout=30)
        try:
            return r.json()
        except:
            return {"text": r.text}
    except Exception as e:
        return {"error": str(e)}
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting PaperLens Backend...")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

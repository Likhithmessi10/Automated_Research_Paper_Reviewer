# api.py
from fastapi import FastAPI, UploadFile, File, Form
from review_model import review_pdf
import shutil
import os

app = FastAPI()

@app.post("/analyze")
async def analyze_paper(
    file: UploadFile = File(...), 
    rewrite: bool = Form(True)
):
    # Save uploaded file temporarily
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Call your existing logic
        # Ensure ollama is running: 'ollama serve'
        results = review_pdf(temp_filename, rewrite=rewrite, ollama_model="llama3.1:8b")

        # Return just the text report for simplicity in the mobile app
        return {"report": results["report"]}
    except Exception as e:
        return {"report": f"Error: {str(e)}"}
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# Run with: uvicorn api:app --host 0.0.0.0 --port 8000
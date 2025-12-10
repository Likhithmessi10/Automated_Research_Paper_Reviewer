import requests
from bs4 import BeautifulSoup

def check_plagiarism_smallseotools(text: str):
    """
    Free web-based plagiarism check using SmallSEOTools.
    Returns:
        plagiarism_percent (int),
        originality_percent (int),
        risk_level (str)
    """

    # SmallSEOTools expects form-style POST
    url = "https://smallseotools.com/plagiarism-checker/"
    
    payload = {
        "input": text[:1500]  # keep it short to avoid rejection
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=20)

        if response.status_code != 200:
            return 0, 100, "UNKNOWN"

        soup = BeautifulSoup(response.text, "html.parser")

        # These selectors are approximate (site may change UI)
        plagiarism_value = 0
        originality_value = 100

        for tag in soup.find_all("span"):
            if "Plagiarism" in tag.text:
                plagiarism_value = int(
                    tag.find_next("span").text.replace("%", "").strip()
                )
            if "Original" in tag.text:
                originality_value = int(
                    tag.find_next("span").text.replace("%", "").strip()
                )

        # Risk Level Logic
        if plagiarism_value < 15:
            risk = "LOW"
        elif plagiarism_value < 35:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        return plagiarism_value, originality_value, risk

    except Exception:
        # Fallback if site blocks or times out
        return 0, 100, "UNAVAILABLE"
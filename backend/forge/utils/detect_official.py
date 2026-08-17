"""URL classifier — routes known official-API domains away from browser forging.

Rules (keep in sync with frontend/src/utils/detectOfficial.ts):
  amazon             -> CUSTOM  "amazon"   (covered by the hardcoded amazon core)
  mail.google/gmail  -> OFFICIAL "gmail"   (official Gmail SMTP/API — never forge)
  notion             -> OFFICIAL "notion"  (official Notion API — never forge)
  anything else      -> CUSTOM  url        (scout + LLM forge, 2 tools per site)
"""

OFFICIAL_KEYWORDS = ["mail.google", "gmail", "notion.com", "notion.so"]


def classify_url(url: str) -> dict:
    url_low = (url or "").lower()
    if "amazon" in url_low:
        return {"type": "CUSTOM", "name": "amazon"}
    if any(k in url_low for k in ["mail.google", "gmail"]):
        return {"type": "OFFICIAL", "name": "gmail"}
    if "notion" in url_low:
        return {"type": "OFFICIAL", "name": "notion"}
    return {"type": "CUSTOM", "name": url}

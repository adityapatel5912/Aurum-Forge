"""URL classifier — routes known official-API domains away from browser forging.

Rules (keep in sync with frontend/src/utils/detectOfficial.ts):
  amazon             -> CUSTOM  "amazon"   (covered by the hardcoded amazon core)
  mail.google/gmail  -> OFFICIAL "gmail"   (official Gmail SMTP/API — never forge)
  notion             -> OFFICIAL "notion"  (official Notion API — never forge)
  telegram / t.me    -> OFFICIAL "telegram"
  instagram          -> OFFICIAL "instagram"
  youtube / youtu.be -> OFFICIAL "youtube"
  github             -> OFFICIAL "github"
  slack              -> OFFICIAL "slack"
  anything else      -> CUSTOM  url        (scout + LLM forge, 2 tools per site)
"""

OFFICIAL_KEYWORDS = [
    "mail.google", "gmail", "notion.com", "notion.so",
    "t.me", "telegram.org", "instagram.com", "youtube.com", "youtu.be",
    "github.com", "slack.com"
]


def classify_url(url: str) -> dict:
    url_low = (url or "").lower()
    if "amazon" in url_low:
        return {"type": "CUSTOM", "name": "amazon"}
    if any(k in url_low for k in ["mail.google", "gmail"]):
        return {"type": "OFFICIAL", "name": "gmail"}
    if "notion" in url_low:
        return {"type": "OFFICIAL", "name": "notion"}
    if any(k in url_low for k in ["t.me", "telegram"]):
        return {"type": "OFFICIAL", "name": "telegram"}
    if "instagram" in url_low:
        return {"type": "OFFICIAL", "name": "instagram"}
    if any(k in url_low for k in ["youtube.com", "youtu.be"]):
        return {"type": "OFFICIAL", "name": "youtube"}
    if "github.com" in url_low:
        return {"type": "OFFICIAL", "name": "github"}
    if "slack.com" in url_low:
        return {"type": "OFFICIAL", "name": "slack"}
    return {"type": "CUSTOM", "name": url}

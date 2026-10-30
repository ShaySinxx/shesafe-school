"""Rule-based knowledge base. Independent of the AI module.
To add a category: drop a new JSON file in /knowledge (same fields as the others)."""
import json
from pathlib import Path

DIR = Path(__file__).parent / "knowledge"

CORE_RESOURCES = [
    {"name": "Emergency response (police, medical, fire)", "contact": "112"},
    {"name": "Childline (free helpline for children)", "contact": "1098"},
]
DEFAULT_SCHOOL = ["Class teacher or mentor", "School counsellor", "Principal or school safeguarding staff"]
DISCLAIMERS = [
    "This app is not an emergency service, counselling, or an official reporting channel.",
    "Confidentiality cannot be promised. Your message is not saved by this app, but trusted adults or schools may need to act to keep you safe.",
    "Contacts and rules can change. Please confirm them with your school or the official websites.",
]
KEYWORDS = {  # priority order: first match wins
    "sexual-harassment-assault": ["sexual", "touched", "molest", "rape", "assault", "inappropriate", "nude", "groped"],
    "deepfakes-impersonation": ["deepfake", "fake account", "fake profile", "edited photo", "morph", "impersonat", "pretending to be me", "ai generated"],
    "stalking": ["stalk", "following me", "follows me", "watching me"],
    "threats": ["threat", "will hurt", "will kill", "warned me"],
    "physical-violence": ["hit me", "beat me", "beaten", "slap", "punch", "kicked", "pushed me", "physically"],
    "discrimination": ["discriminat", "caste", "religion", "racist", "unfair treatment", "because of my"],
    "cyberbullying": ["online", "instagram", "whatsapp", "snapchat", "group chat", "social media", "cyber", "troll"],
    "harassment": ["harass"],
    "bullying": ["bully", "bullied", "teased", "teasing", "left out", "excluded", "rumour", "rumor", "name calling"],
}


def load_all():
    guides = {}
    for f in sorted(DIR.glob("*.json")):
        try:
            g = json.loads(f.read_text(encoding="utf-8"))
            guides[g["slug"]] = g
        except Exception:
            continue
    return guides


def get_guide(slug):
    g = load_all().get(slug)
    if g:
        g = {**g, "disclaimers": DISCLAIMERS + ([g["disclaimer"]] if g.get("disclaimer") else [])}
    return g


def classify(text):
    t = text.lower()
    guides = load_all()
    for slug, words in KEYWORDS.items():
        if slug in guides and any(w in t for w in words):
            return slug
    return None

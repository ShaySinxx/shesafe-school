"""Independent safety pre-check. Runs BEFORE any AI call.
Keyword matching is only a first layer, not a complete safety system."""
import re
import knowledge

URGENT = [
    r"suicid", r"\b(kill|hurt|harm|cut) (myself|my self)\b", r"\bend my (own )?life\b", r"\bend it all\b",
    r"\bwant(s|ed)? to die\b", r"\b(don'?t|do not) want to (live|be alive|exist)\b", r"\bbetter off dead\b",
    r"\b(is|are) (going to|gonna|about to) (kill|rape|stab|shoot) me\b", r"\b(raping|molesting) me\b",
    r"\b(in danger|unsafe) (right )?now\b", r"\bmarna chah(ta|ti)\b", r"\bjaan de (dunga|dungi)\b",
]
ELEVATED = [
    r"\brap(e|ed)\b", r"molest", r"\bsexual", r"touched me", r"\bnude", r"\bnaked", r"intimate (photo|image|pic)",
    r"blackmail", r"threat", r"\bweapon", r"\bgun\b", r"\bknife\b", r"beaten", r"hit me", r"stalk", r"following me",
    r"deepfake", r"self.?harm", r"hopeless", r"can'?t take it", r"scared for my life", r"\babuse",
]


def _norm(text):
    return re.sub(r"\s+", " ", text.lower().replace("\u2019", "'")).strip()


def check(text):
    t = _norm(text)
    if any(re.search(p, t) for p in URGENT):
        return "urgent"
    if any(re.search(p, t) for p in ELEVATED):
        return "elevated"
    return "normal"


def urgent_response():
    return {
        "mode": "urgent",
        "category": "Urgent safety concern",
        "summary": "What you wrote suggests that you or someone else may be in danger or in serious distress. You deserve help from a real person right now.",
        "seriousness": "urgent",
        "actions": [
            "If you are in immediate danger, call 112 now.",
            "Move to a safe place near other people, and tell a trusted adult right now: a parent, teacher, counsellor or neighbour.",
            "You can also call Childline 1098 to talk to someone.",
            "If you are having thoughts of ending your life, please contact Tele-MANAS 14416 or tell an adult near you today.",
        ],
        "support": {
            "school": knowledge.DEFAULT_SCHOOL,
            "official": knowledge.CORE_RESOURCES + [{"name": "Tele-MANAS mental health helpline", "contact": "14416"}],
        },
        "emergency_banner": True,
        "disclaimers": knowledge.DISCLAIMERS,
    }

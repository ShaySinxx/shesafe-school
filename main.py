from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()
import ai_client, knowledge, safety  # noqa: E402

BASE = Path(__file__).parent
app = FastAPI(title="Student Safety Support (MVP)")
app.mount("/static", StaticFiles(directory=BASE / "static", check_dir=False), name="static")

RANK = {"low": 0, "moderate": 1, "serious": 2, "urgent": 3}
GENERIC_ACTIONS = [
    "Talk to a trusted adult today, such as a parent, teacher or school counsellor.",
    "Write down what happened, when, and who was there.",
    "Stay near people you trust and avoid being alone with anyone who makes you uncomfortable.",
    "Do not share or forward intimate images, and do not reply to threats.",
    "If you ever feel in danger, call 112.",
]


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


def build(mode, slug, summary, seriousness, actions, level):
    g = knowledge.get_guide(slug) if slug else None
    if level == "elevated" and RANK[seriousness] < 2:
        seriousness = "serious"
    actions = list(actions)
    if level == "elevated":
        actions.insert(0, "Please talk to a trusted adult today. You do not have to handle this alone.")
    return {
        "mode": mode,
        "category": g["title"] if g else "Other / not sure",
        "summary": summary,
        "seriousness": seriousness,
        "actions": actions[:6],
        "support": {
            "school": g["school_support"] if g else knowledge.DEFAULT_SCHOOL,
            "official": knowledge.CORE_RESOURCES + (g["official_resources"] if g else []),
        },
        "emergency_banner": seriousness in ("serious", "urgent"),
        "disclaimers": g["disclaimers"] if g else knowledge.DISCLAIMERS,
    }


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "Please describe your concern.")
    level = safety.check(text)
    if level == "urgent":  # no AI call at all
        return safety.urgent_response()
    provider, result = await ai_client.analyze(text)
    if result:
        slug = result["category"] if result["category"] != "other" else None
        return build("ai", slug, result["summary"], result["seriousness"], result["actions"], level)
    # Guaranteed local fallback (no network needed)
    slug = knowledge.classify(text)
    g = knowledge.get_guide(slug) if slug else None
    if g:
        summary = f"This may be about {g['title'].lower()}. A built-in guide is shown because the AI service was unavailable."
        return build("fallback", slug, summary, g.get("default_seriousness", "moderate"), g["steps"][:5], level)
    summary = "A built-in guide is shown because the AI service was unavailable. Here are safe first steps."
    return build("fallback", None, summary, "moderate", GENERIC_ACTIONS, level)


@app.get("/api/guides")
def list_guides():
    return [{"slug": s, "title": g["title"], "meaning": g["meaning"]} for s, g in knowledge.load_all().items()]


@app.get("/api/guides/{slug}")
def one_guide(slug: str):
    g = knowledge.get_guide(slug)
    if not g:
        raise HTTPException(404, "Guide not found")
    return g


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/")
def home():
    idx = BASE / "static" / "index.html"
    return FileResponse(idx) if idx.exists() else {"status": "backend running", "docs": "/docs"}

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# == SOURCE BIAS SCORES ==

US_SOURCE_BIAS = {
    "fox-news": 0.7,
    "breitbart": 0.9,
    "cnn": -0.4,
    "npr": -0.3,
    "bbc-news": -0.1,
    "reuters": 0.0,
    "associated-press": 0.0,
    "msnbc": -0.7,
    "the-guardian": -0.5,
    "gizmodo.com": -0.3,
    "usa-today": -0.1,
    "the-verge": -0.2,
    "slate-magazine": -0.4,
}

APAC_SOURCE_BIAS = {
    "abc-news-au": -0.2,
    "the-australian": 0.6,
    "sydney-morning-herald": -0.3,
    "sky-news-australia": 0.7,
    "xinhua": 1.0,
    "china-daily": 0.9,
    "global-times": 0.95,
    "scmp": 0.2,
    "rnz": -0.1,
    "abc-pacific": -0.1,
    "islands-business": 0.0,
    "rnz-pacific": -0.1,
}

ALL_SOURCES = {**US_SOURCE_BIAS, **APAC_SOURCE_BIAS}

# == POLITICAL WORD LISTS ==

US_LEFT_WORDS = [
    "climate justice", "systemic racism", "gun control",
    "reproductive rights", "wealth inequality", "social justice",
    "universal healthcare", "defund", "marginalized"
]

US_RIGHT_WORDS = [
    "border security", "free market", "election integrity",
    "mainstream media", "deep state", "second amendment",
    "traditional values", "big government", "socialism"
]

AUS_LEFT_WORDS = [
    "labor party", "union rights", "medicare",
    "indigenous rights", "renewable energy",
    "affordable housing", "welfare"
]

AUS_RIGHT_WORDS = [
    "liberal party", "coalition", "lower taxes",
    "border protection", "stop the boats",
    "small government", "religious freedom"
]

PRO_CCP_WORDS = [
    "common prosperity", "core socialist values",
    "national rejuvenation", "reunification",
    "one china", "century of humiliation",
    "wolf warrior"
]

CRITICAL_CCP_WORDS = [
    "human rights", "uyghur", "taiwan independence",
    "tiananmen", "hong kong democracy",
    "xinjiang", "surveillance state",
    "authoritarianism"
]

PRO_PACIFIC_WORDS = [
    "ocean sovereignty", "pacific way",
    "climate vulnerability", "rising sea levels",
    "indigenous sovereignty", "decolonization",
    "pacific regionalism"
]

PRO_DEVELOPMENT_WORDS = [
    "belt and road", "infrastructure investment",
    "economic development", "fishing rights",
    "security agreement", "china pacific"
]

# == MODELS ==

class BiasScores(BaseModel):
    us_bias: float = 0.0
    aus_bias: float = 0.0
    china_bias: float = 0.0
    pacific_bias: float = 0.0

class Article(BaseModel):
    title: str
    description: Optional[str] = ""
    source: dict
    url: str
    publishedAt: str
    bias_score: float = 0.0
    regional_scores: Optional[BiasScores] = None

class ScoreRequest(BaseModel):
    articles: List[Article]

# == SCORING FUNCTIONS ==

def scan_words(text: str, word_list: list, direction: float) -> float:
    score = 0.0
    for word in word_list:
        if word in text:
            score += direction * 0.1
    return score

def get_regional_scores(source_id: str, title: str, description: str) -> BiasScores:
    text = f"{title} {description}".lower()
    source = source_id.lower()

    us_source = US_SOURCE_BIAS.get(source, 0.0)
    us_content = scan_words(text, US_LEFT_WORDS, -1) + scan_words(text, US_RIGHT_WORDS, 1)
    us_final = (us_source * 0.6) + (us_content * 0.4)

    aus_source = APAC_SOURCE_BIAS.get(source, 0.0)
    aus_content = scan_words(text, AUS_LEFT_WORDS, -1) + scan_words(text, AUS_RIGHT_WORDS, 1)
    aus_final = (aus_source * 0.6) + (aus_content * 0.4)

    china_content = scan_words(text, CRITICAL_CCP_WORDS, -1) + scan_words(text, PRO_CCP_WORDS, 1)
    china_final = china_content

    pacific_content = scan_words(text, PRO_PACIFIC_WORDS, -1) + scan_words(text, PRO_DEVELOPMENT_WORDS, 1)
    pacific_final = pacific_content

    def clamp(val):
        return round(max(-1.0, min(1.0, val)), 2)

    return BiasScores(
        us_bias=clamp(us_final),
        aus_bias=clamp(aus_final),
        china_bias=clamp(china_final),
        pacific_bias=clamp(pacific_final),
    )

# == ROUTES ==

@app.get("/")
def root():
    return {"message": "Herekam Bias Scorer is running!"}

@app.post("/score")
def score_articles(request: ScoreRequest):
    scored = []
    for article in request.articles:
        source_id = article.source.get("id", "")
        scores = get_regional_scores(
            source_id,
            article.title,
            article.description or ""
        )
        article.regional_scores = scores
        article.bias_score = scores.us_bias
        scored.append(article)
    return {"articles": scored}
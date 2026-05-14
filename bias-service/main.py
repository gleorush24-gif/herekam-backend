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
    "foxnews.com": 0.7,
    "npr.org": -0.3,
    "bbc.co.uk": -0.1,
    "theguardian.com": -0.5,
    "breitbart.com": 0.9,
    "msnbc.com": -0.7,
    "cnn.com": -0.4,
    "nytimes.com": -0.3,
    "washingtonpost.com": -0.3,
    "wsj.com": 0.3,
    "thehill.com": 0.1,
    "politico.com": -0.1,
    "axios.com": 0.0,
    "reuters.com": 0.0,
    "apnews.com": 0.0,
    "wired.com": -0.2,
    "theatlantic.com": -0.3,
    "nationalreview.com": 0.6,
    "thedailywire.com": 0.8,
    "thedailybeast.com": -0.4,
    "slate.com": -0.4,
    "vox.com": -0.5,
    "motherjones.com": -0.7,
    "reason.com": 0.4,
    "nypost.com": 0.6,
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
    "smh.com.au": -0.3,
    "theaustralian.com.au": 0.6,
    "abc.net.au": -0.2,
    "skynews.com.au": 0.7,
    "9news.com.au": 0.0,
    "news.com.au": 0.2,
    "globaltimes.cn": 0.95,
    "xinhuanet.com": 1.0,
    "scmp.com": 0.2,
    "rnz.co.nz": -0.1,
}

ALL_SOURCES = {**US_SOURCE_BIAS, **APAC_SOURCE_BIAS}

# == POLITICAL WORD LISTS ==

US_LEFT_WORDS = [
    "climate justice", "systemic racism", "gun control",
    "reproductive rights", "wealth inequality", "social justice",
    "universal healthcare", "defund", "marginalized",
    "white privilege", "intersectionality", "equity",
    "pro-choice", "transgender rights", "living wage",
    "medicare for all", "green new deal", "police reform"
]

US_RIGHT_WORDS = [
    "border security", "free market", "election integrity",
    "mainstream media", "deep state", "second amendment",
    "traditional values", "big government", "socialism",
    "pro-life", "illegal alien", "radical left",
    "cancel culture", "woke", "patriot",
    "law and order", "make america great", "america first"
]

AUS_LEFT_WORDS = [
    "labor party", "union rights", "medicare",
    "indigenous rights", "renewable energy",
    "affordable housing", "welfare", "albo",
    "albanese", "greens policy", "teal independent"
]

AUS_RIGHT_WORDS = [
    "liberal party", "coalition", "lower taxes",
    "border protection", "stop the boats",
    "small government", "religious freedom",
    "dutton", "morrison", "national party"
]

PRO_CCP_WORDS = [
    "common prosperity", "core socialist values",
    "national rejuvenation", "reunification",
    "one china", "century of humiliation",
    "wolf warrior", "chinese dream", "xi jinping thought"
]

CRITICAL_CCP_WORDS = [
    "human rights", "uyghur", "taiwan independence",
    "tiananmen", "hong kong democracy",
    "xinjiang", "surveillance state",
    "authoritarianism", "crackdown", "oppression"
]

PRO_PACIFIC_WORDS = [
    "ocean sovereignty", "pacific way",
    "climate vulnerability", "rising sea levels",
    "indigenous sovereignty", "decolonization",
    "pacific regionalism", "pacific islands forum",
    "solomon islands", "fiji", "vanuatu", "samoa"
]

PRO_DEVELOPMENT_WORDS = [
    "belt and road", "infrastructure investment",
    "economic development", "fishing rights",
    "security agreement", "china pacific",
    "chinese investment", "port development"
]

# == FRAMING WORDS (NEW!) ==
# These detect HOW the article is written not just what it covers

NEGATIVE_FRAMING = [
    "failed", "crisis", "disaster", "corrupt",
    "scandal", "chaos", "threat", "dangerous",
    "extreme", "radical", "alarming"
]

POSITIVE_FRAMING = [
    "success", "growth", "strong", "secure",
    "protected", "thriving", "winning", "great",
    "patriot", "brave", "freedom"
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

def get_framing_score(text: str) -> float:
    negative = scan_words(text, NEGATIVE_FRAMING, 1)
    positive = scan_words(text, POSITIVE_FRAMING, -1)
    return negative + positive

def get_regional_scores(source_id: str, title: str, description: str) -> BiasScores:
    text = f"{title} {description}".lower()
    source = source_id.lower()

    source_score = ALL_SOURCES.get(source, 0.0)
    us_content = scan_words(text, US_LEFT_WORDS, -1) + scan_words(text, US_RIGHT_WORDS, 1)
    framing = get_framing_score(text)
    us_final = (source_score * 0.6) + (us_content * 0.3) + (framing * 0.1)

    aus_source = APAC_SOURCE_BIAS.get(source, 0.0)
    aus_content = scan_words(text, AUS_LEFT_WORDS, -1) + scan_words(text, AUS_RIGHT_WORDS, 1)
    aus_final = (aus_source * 0.6) + (aus_content * 0.3) + (framing * 0.1)

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
        source_name = article.source.get("name", "")
        if not source_id:
            source_id = source_name.lower().replace(" ", "-")

        scores = get_regional_scores(
            source_id,
            article.title,
            article.description or ""
        )
        article.regional_scores = scores
        article.bias_score = scores.us_bias
        scored.append(article)

    return {"articles": scored}

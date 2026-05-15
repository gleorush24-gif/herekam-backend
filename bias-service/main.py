from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from urllib.parse import urlparse

app = FastAPI()

# == SOURCE BIAS SCORES ==

US_SOURCE_BIAS = {
    "breitbart": 0.95,
    "breitbart.com": 0.95,
    "thedailywire.com": 0.85,
    "dailywire.com": 0.85,
    "thedailywire": 0.85,
    "oann.com": 0.9,
    "newsmax.com": 0.8,
    "newsmax": 0.8,
    "thegatewaypundit.com": 0.95,
    "westernjournal.com": 0.8,
    "thefederalist.com": 0.75,
    "washingtonexaminer.com": 0.6,
    "washingtonexaminer": 0.6,
    "nypost.com": 0.6,
    "nypost": 0.6,
    "nationalreview.com": 0.6,
    "nationalreview": 0.6,
    "reason.com": 0.4,
    "fox-news": 0.7,
    "foxnews.com": 0.7,
    "fox-news.com": 0.7,
    "wsj.com": 0.3,
    "wall-street-journal": 0.3,
    "thehill.com": 0.1,
    "the-hill": 0.1,
    "realclearpolitics.com": 0.3,
    "forbes.com": 0.2,
    "spectator.co.uk": 0.5,
    "telegraph.co.uk": 0.5,
    "thetimes.co.uk": 0.3,
    "reuters": 0.0,
    "reuters.com": 0.0,
    "associated-press": 0.0,
    "apnews.com": 0.0,
    "axios.com": 0.0,
    "axios": 0.0,
    "politico.com": -0.1,
    "politico": -0.1,
    "bbc-news": -0.1,
    "bbc.co.uk": -0.1,
    "bbc.com": -0.1,
    "npr": -0.3,
    "npr.org": -0.3,
    "pbs.org": -0.2,
    "csmonitor.com": 0.0,
    "usatoday.com": -0.1,
    "usa-today": -0.1,
    "nytimes.com": -0.3,
    "new-york-times": -0.3,
    "washingtonpost.com": -0.3,
    "washington-post": -0.3,
    "theatlantic.com": -0.3,
    "the-atlantic": -0.3,
    "time.com": -0.2,
    "nbcnews.com": -0.3,
    "nbcnews": -0.3,
    "abcnews.go.com": -0.3,
    "abc-news": -0.3,
    "cbsnews.com": -0.3,
    "cbsnews": -0.3,
    "msnbc.com": -0.7,
    "msnbc": -0.7,
    "cnn.com": -0.4,
    "cnn": -0.4,
    "wired.com": -0.2,
    "wired": -0.2,
    "theverge.com": -0.2,
    "the-verge": -0.2,
    "gizmodo.com": -0.3,
    "buzzfeednews.com": -0.4,
    "huffpost.com": -0.5,
    "huffingtonpost.com": -0.5,
    "thedailybeast.com": -0.4,
    "salon.com": -0.5,
    "rawstory.com": -0.6,
    "slate.com": -0.4,
    "slate-magazine": -0.4,
    "vox.com": -0.5,
    "motherjones.com": -0.7,
    "thenation.com": -0.7,
    "jacobin.com": -0.9,
    "theguardian.com": -0.5,
    "the-guardian": -0.5,
    "guardian.com": -0.5,
    "democracynow.org": -0.8,
    "commondreams.org": -0.8,
    "alternet.org": -0.7,
    "truthout.org": -0.7,
    "bloomberg.com": 0.1,
    "bloomberg": 0.1,
    "ft.com": 0.2,
    "financial-times": 0.2,
    "marketwatch.com": 0.1,
    "cnbc.com": 0.1,
    "cnbc": 0.1,
    "businessinsider.com": -0.1,
    "techcrunch.com": -0.2,
    "arstechnica.com": -0.2,
    "engadget.com": -0.2,
    "cnet.com": -0.1,
}

APAC_SOURCE_BIAS = {
    "the-australian": 0.6,
    "theaustralian.com.au": 0.6,
    "sky-news-australia": 0.7,
    "skynews.com.au": 0.7,
    "news.com.au": 0.2,
    "heraldsun.com.au": 0.5,
    "couriermail.com.au": 0.5,
    "dailytelegraph.com.au": 0.5,
    "adelaidenow.com.au": 0.3,
    "perthnow.com.au": 0.3,
    "spectator.com.au": 0.6,
    "abc-news-au": -0.2,
    "abc.net.au": -0.2,
    "sydney-morning-herald": -0.3,
    "smh.com.au": -0.3,
    "theage.com.au": -0.3,
    "crikey.com.au": -0.4,
    "9news.com.au": 0.0,
    "7news.com.au": 0.0,
    "sbs.com.au": -0.2,
    "michaelwest.com.au": -0.5,
    "rnz.co.nz": -0.1,
    "rnz": -0.1,
    "rnz-pacific": -0.1,
    "stuff.co.nz": -0.1,
    "nzherald.co.nz": 0.1,
    "newshub.co.nz": -0.1,
    "abc-pacific": -0.1,
    "islands-business": 0.0,
    "islandsbusiness.com": 0.0,
    "rnzpacific.co.nz": -0.1,
    "pina.com.fj": 0.0,
    "solomonstarnews.com": 0.0,
    "islandsun.com.sb": 0.0,
    "xinhua": 1.0,
    "xinhuanet.com": 1.0,
    "china-daily": 0.9,
    "chinadaily.com.cn": 0.9,
    "global-times": 0.95,
    "globaltimes.cn": 0.95,
    "cgtn.com": 0.9,
    "people.com.cn": 0.95,
    "scmp": 0.2,
    "scmp.com": 0.2,
    "straitstimes.com": 0.1,
    "channelnewsasia.com": 0.0,
    "japantimes.co.jp": 0.0,
    "koreaherald.com": 0.0,
    "hindustantimes.com": 0.1,
    "timesofindia.com": 0.1,
    "aljazeera.com": -0.2,
    "aljazeera": -0.2,
    "middleeasteye.net": -0.3,
}

ALL_SOURCES = {**US_SOURCE_BIAS, **APAC_SOURCE_BIAS}

# == POLITICAL WORD LISTS ==

US_LEFT_WORDS = [
    "climate justice", "systemic racism", "gun control",
    "reproductive rights", "wealth inequality", "social justice",
    "universal healthcare", "defund", "marginalized",
    "white privilege", "intersectionality", "equity",
    "pro-choice", "transgender rights", "living wage",
    "medicare for all", "green new deal", "police reform",
    "abolish ice", "reparations", "affirmative action",
    "income inequality", "gender pay gap", "racial equity",
    "lgbtq rights", "hate crime", "voter suppression",
    "dark money", "corporate greed", "tax the rich",
    "billionaire", "student debt", "workers rights",
    "unions", "collective bargaining", "minimum wage",
    "housing justice", "food insecurity", "mass incarceration",
    "criminal justice reform", "implicit bias", "microaggression",
    "safe space", "trigger warning", "cultural appropriation",
]

US_RIGHT_WORDS = [
    "border security", "free market", "election integrity",
    "mainstream media", "deep state", "second amendment",
    "traditional values", "big government", "socialism",
    "pro-life", "illegal alien", "radical left",
    "cancel culture", "woke", "patriot",
    "law and order", "make america great", "america first",
    "fake news", "witch hunt", "hoax",
    "antifa", "far left", "marxist",
    "open borders", "illegal immigration", "sanctuary city",
    "religious liberty", "gun rights", "constitutional",
    "lower taxes", "deregulation", "small government",
    "strong military", "energy independence",
    "voter id", "election fraud", "stolen election",
    "critical race theory", "indoctrination", "parental rights",
    "biological sex", "big tech censorship", "free speech",
]

AUS_LEFT_WORDS = [
    "labor party", "union rights", "medicare",
    "indigenous rights", "renewable energy",
    "affordable housing", "welfare", "albo",
    "albanese", "greens policy", "teal independent",
    "aboriginal", "first nations", "treaty",
    "climate action", "carbon tax", "emissions target",
    "wage theft", "penalty rates", "casual workers",
    "refugees", "asylum seekers", "offshore detention",
    "republic", "reconciliation",
]

AUS_RIGHT_WORDS = [
    "liberal party", "coalition", "lower taxes",
    "border protection", "stop the boats",
    "small government", "religious freedom",
    "dutton", "morrison", "national party",
    "economic management", "budget surplus",
    "deregulation", "mining industry", "coal jobs",
    "anti-woke", "family values",
    "national security", "defense spending",
    "illegal boat arrivals", "immigration control",
]

PRO_CCP_WORDS = [
    "common prosperity", "core socialist values",
    "national rejuvenation", "reunification",
    "one china", "century of humiliation",
    "wolf warrior", "chinese dream", "xi jinping thought",
    "chinese sovereignty", "non-interference",
    "win-win cooperation", "peaceful development",
    "chinese model", "harmonious society",
]

CRITICAL_CCP_WORDS = [
    "human rights", "uyghur", "taiwan independence",
    "tiananmen", "hong kong democracy",
    "xinjiang", "surveillance state",
    "authoritarianism", "crackdown", "oppression",
    "forced labor", "concentration camp", "genocide",
    "censorship", "great firewall", "dissidents",
    "tibet", "dalai lama", "falun gong",
    "social credit", "mass surveillance",
]

PRO_PACIFIC_WORDS = [
    "ocean sovereignty", "pacific way",
    "climate vulnerability", "rising sea levels",
    "indigenous sovereignty", "decolonization",
    "pacific regionalism", "pacific islands forum",
    "solomon islands", "fiji", "vanuatu", "samoa",
    "tuvalu", "kiribati", "marshall islands",
    "blue pacific", "oceania", "melanesia",
    "polynesia", "micronesia", "pacific culture",
    "traditional fishing", "exclusive economic zone",
    "small island developing states", "loss and damage",
    "climate refugees", "pacific voices",
]

PRO_DEVELOPMENT_WORDS = [
    "belt and road", "infrastructure investment",
    "economic development", "fishing rights",
    "security agreement", "china pacific",
    "chinese investment", "port development",
    "debt trap", "development aid", "trade agreement",
    "bri", "silk road", "chinese loans",
    "wharf development", "airport development",
    "police cooperation", "security pact",
]

NEGATIVE_FRAMING = [
    "failed", "crisis", "disaster", "corrupt",
    "scandal", "chaos", "threat", "dangerous",
    "extreme", "radical", "alarming", "shocking",
    "outrage", "slammed", "blasted", "attacked",
    "collapsed", "destroyed", "ruined", "broken",
    "incompetent", "lies", "lied", "deceived",
]

POSITIVE_FRAMING = [
    "success", "growth", "strong", "secure",
    "protected", "thriving", "winning", "great",
    "patriot", "brave", "freedom", "triumph",
    "victory", "booming", "record", "historic",
    "landmark", "breakthrough", "achievement",
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

def get_regional_scores(source_id: str, title: str, description: str, domain: str = "") -> BiasScores:
    text = f"{title} {description}".lower()
    source = source_id.lower()

    source_score = ALL_SOURCES.get(source, ALL_SOURCES.get(domain, 0.0))
    us_content = scan_words(text, US_LEFT_WORDS, -1) + scan_words(text, US_RIGHT_WORDS, 1)
    framing = get_framing_score(text)
    us_final = (source_score * 0.6) + (us_content * 0.3) + (framing * 0.1)

    aus_source = APAC_SOURCE_BIAS.get(source, APAC_SOURCE_BIAS.get(domain, 0.0))
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

        # Extract domain from URL
        domain = ""
        try:
            parsed = urlparse(article.url)
            domain = parsed.netloc.replace("www.", "")
        except:
            pass

        # Try source_id first then source_name then domain
        if not source_id:
            source_id = source_name.lower().replace(" ", "-")

        scores = get_regional_scores(
            source_id,
            article.title,
            article.description or "",
            domain
        )
        article.regional_scores = scores
        article.bias_score = scores.us_bias
        scored.append(article)

    return {"articles": scored}

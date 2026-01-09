
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="Backlink Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def parse_backlinks(html):
    soup = BeautifulSoup(html, "html.parser")

    stats = {}
    for block in soup.select(".statistic"):
        value = block.find("h3").get_text(strip=True).replace(",", "")
        label = block.find("span").get_text(strip=True).lower()
        stats[label] = int(value)

    backlinks = []
    for tr in soup.select("#backlinks tbody tr"):
        tds = tr.find_all("td")
        backlinks.append({
            "page_title": tds[1].select_one("strong[data-key='title']").get_text(strip=True),
            "source_url": tds[1].select_one("a[data-key='url']")["href"],
            "anchor_text": tds[2].select_one("strong[data-key='title']").get_text(strip=True),
            "target_url": tds[2].select_one("a[data-key='url']")["href"],
            "pa": int(tds[3].select_one(".value").text),
            "da": int(tds[4].select_one(".value").text),
            "found_date": tds[5].get_text(strip=True)
        })

    return stats, backlinks


@app.get("/")
def health_check():
    return {"status": "Backend running"}


@app.get("/analyze")
def analyze(domain: str):
    url = "https://rankifyer.com/free-seo-tools/embed"

    params = {
        "id": "high-quality-backlinks",
        "ref": "https://rankifyer.com/backlink-checker/",
        "ref_hash": "ffd9bb20bb21736b47a1de5a39d1cdd3d382adcb50991497866ca45107878088",
        "h": "0",
        "r": "423b01",
        "site": domain,
        "exp": "1767834165"
    }

    headers = {
        "user-agent": "Mozilla/5.0",
        "accept": "text/html"
    }

    response = requests.get(url, params=params, headers=headers, timeout=30)

    if response.status_code != 200:
        return {"error": "Failed to fetch data"}

    stats, backlinks = parse_backlinks(response.text)

    return {
        "domain": domain,
        "stats": stats,
        "backlinks": backlinks
    }

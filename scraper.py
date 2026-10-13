import requests
import time
import bs4 from BeautifulSoup
from config import USERNAME, COOKIES, REQUEST_DELAY

BASE_URL = "https://archiveofourown.org"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36 "
}

def get_page(page: int, debug: bool = False) -> BeautifulSoup | None:
    url = f"{BASE_URL}/users/{USERNAME}/readings?page={page}"
    try:
        r = requests.get(url, cookies=COOKIES, headers=HEADERS, timeout=15)
        if r.status_code == 429:
            print("Rate limited, waiting 60s...")
            time.sleep(60)
            r = requests.get(url, cookies=COOKIES, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"Error {r.status_code} on page {page}")
            return None
        soup = BeautifulSoup(r.text, "lxml")
        if debug:
            _debug(soup, page)
        return soup
    except Expection as e:
        print(f"Equest failed on page {page}: {e}")
        return None

def _debug(soup: BeautifulSoup, page: int):
    print(f"\n  [DEBUG page {page}]")
    logged_in = soup.select_one("a[href*='/logout']")
    print(f"  Logged in: {'YES' if logged_in else 'NO — cookies invalid or expired!'}")
    title = soup.select_one("title")
    print(f"  Page title: {title.get_text(strip=True) if title else 'none'}")
    for sel in ["li.reading.work", "li.work", "#main ol li"]:
        found = soup.select(sel)
        if found:
            print(f"  Selector '{sel}': {len(found)} elements")
    main = soup.select_one("#main")
    if main:
        print(f"  #main snippet: {main.get_text(separator=' ', strip=True)[:300]}")
    print() 

def detect_total_pages(soup: BeautifulSoup) -> int:
    """Read AO3's pagination to find the last page number automatically."""
    pages = []
    for a in soup.select("ol.pagination li a"):
        txt = a.get_text(strip=True)
        if txt.isdigit():
            pages.append(int(txt))
    if pages:
        return max(pages)
    return 1

def parse_visits(article) -> int:
    candidates = article.select("p.viewed, h4.viewed, .viewed, p[class*='view'], h4[class*='view']")
    for el in candidates:
        text = el.get_text(separator=" ", strip=True).lower()
        if "visited" in text:
            if "once" in text:
                return 1
            parts = text.split("visited")[-1].split()
            for p in parts:
                if p.isdigit():
                    return int(p)
    full_text = article.get_text(separator=" ", strip=True).lower()
    if "visited once" in full_text:
        return 1
    if "visited" in full_text:
        idx = full_text.find("visited")
        snippet = full_text[idx:idx + 30]
        for p in snippet.split():
            if p.isdigit():
                return int(p)
    return 1

def parse_work(article) -> dict | None:
    try:
        work = {}
 
        title_tag = article.select_one("h4.heading a:first-child")
        if not title_tag:
            title_tag = article.select_one("h4 a, h3 a, .title a")
        if not title_tag:
            return None
 
        work["title"] = title_tag.get_text(strip=True)
        href = title_tag.get("href", "")
        work["id"] = href.split("/works/")[-1].split("/")[0] if "/works/" in href else ""
 
        author_tag = article.select_one("a[rel='author']")
        work["author"] = author_tag.get_text(strip=True) if author_tag else "Anonymous"
 
        work["fandoms"] = [t.get_text(strip=True) for t in article.select("h5.fandoms a.tag, .fandoms a")]
 
        ships, friendships = [], []
        for tag in article.select("li.relationships a.tag"):
            t = tag.get_text(strip=True)
            if "/" in t:
                ships.append(t)
            elif "&" in t:
                friendships.append(t)
        work["ships"] = ships
        work["friendships"] = friendships
 
        work["freeforms"] = [t.get_text(strip=True) for t in article.select("li.freeforms a.tag")]
        work["characters"] = [t.get_text(strip=True) for t in article.select("li.characters a.tag")]
 
        stats = {}
        for dt, dd in zip(article.select("dl.stats dt"), article.select("dl.stats dd")):
            key = dt.get_text(strip=True).lower().rstrip(":")
            stats[key] = dd.get_text(strip=True)
 
        raw_words = stats.get("words", "0").replace(",", "")
        work["word_count"] = int(raw_words) if raw_words.isdigit() else 0
 
        work["language"] = stats.get("language", stats.get("lang", "Unknown"))
 
        req = article.select("ul.required-tags span.text")
        work["rating"]    = req[0].get_text(strip=True) if len(req) > 0 else ""
        work["warnings"]  = req[1].get_text(strip=True) if len(req) > 1 else ""
        work["category"]  = req[2].get_text(strip=True) if len(req) > 2 else ""
        work["complete"]  = req[3].get_text(strip=True) if len(req) > 3 else ""
 
        work["visits"] = parse_visits(article)
 
        date_tag = article.select_one("h4.viewed, p.viewed, .viewed")
        work["last_visited"] = ""
        if date_tag:
            full = date_tag.get_text(strip=True)
            if "Last visited:" in full:
                work["last_visited"] = full.split("Last visited:")[-1].split("|")[0].strip()
 
        return work
 
    except Exception as e:
        print(f"  Parse error: {e}")
        return None
 
 
def _extract_articles(soup: BeautifulSoup) -> list:
    return (
        soup.select("li.reading.work") or
        soup.select("li.work") or
        soup.select("#main ol.index li") or
        soup.select("#main li[id^='work']")
    )
 
 
def scrape_all_history() -> list[dict]:
    all_works = []
    print(f"Scraping history for: {USERNAME}\n")
 
    print("  Fetching page 1 (detecting total pages)...", end=" ")
    soup = get_page(1, debug=True)
    if soup is None:
        print("Failed to load page 1.")
        return []
 
    total_pages = detect_total_pages(soup)
    print(f"  → Total pages detected: {total_pages} (~{total_pages * 20} works)\n")
 
    articles = _extract_articles(soup)
    if not articles:
        print("No works found on page 1. Check the debug output above.")
        return []
 
    for article in articles:
        w = parse_work(article)
        if w:
            all_works.append(w)
    print(f"  Page 1/{total_pages}: {len(articles)} works")
 
    for page in range(2, total_pages + 1):
        print(f"  Page {page}/{total_pages}...", end=" ")
        soup = get_page(page)
        if soup is None:
            print("skipped.")
            continue
 
        articles = _extract_articles(soup)
        if not articles:
            print(f"empty — stopping at page {page - 1}.")
            break
 
        for article in articles:
            w = parse_work(article)
            if w:
                all_works.append(w)
 
        print(f"{len(articles)} works (total: {len(all_works)})")
        time.sleep(REQUEST_DELAY)
 
    print(f"\n✓ Done. {len(all_works):,} works scraped.\n")
    return all_works
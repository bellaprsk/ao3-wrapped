# AO3 Wrapped ✦

> Get a full lifetime reading summary of your Archive of Our Own account — printed right in your terminal.

AO3 Wrapped scrapes your entire reading history and compiles everything: your top ships, fandoms, tags, authors, languages, and a timeline of your reading activity over the years.

---

## What it shows you

| Category | Details |
|---|---|
| 📊 Overview | Total works read, total words, avg words/fic, avg reading time, reread count |
| 📅 Reading over time | Works read per year |
| 🌐 Languages | Top languages across your history |
| ⭐ Ratings | Breakdown by Gen / Teen / Mature / Explicit |
| 💞 Ships & Friendships | Top 10 romantic ships (`/`) and platonic pairs (`&`) |
| 🌍 Fandoms | Top 10 fandoms |
| 🏷️ Tags | Top 20 freeform tags (no character names — only actual tags like Fluff, Angst, Slow Burn…) |
| 🔗 Tag combos | Top 10 most frequent tag pairings |
| ✍️ Authors | Top 10 by fic count and by total words read |
| 📚 Fics | Top 10 longest and top 10 most visited |

---

## Requirements

- Python 3.8 or higher
- A computer with terminal/command line access
- An AO3 account with reading history enabled

---

## Installation

### 1. Clone or download this repository

```bash
git clone https://github.com/bellaprsk/ao3-wrapped.git
cd ao3-wrapped
```

### 2. Install dependencies

```bash
pip install requests beautifulsoup4 lxml rich
```

---

## Setup

### Get your AO3 cookies

The scraper needs your session cookies to access your private reading history. Here's how to grab them:

1. Open your browser and go to [archiveofourown.org](https://archiveofourown.org)
2. Log in to your account
3. Open DevTools — press `F12` on Windows/Linux, or `Cmd + Option + I` on Mac
4. Go to the **Application** tab → **Cookies** → `https://archiveofourown.org`
5. Find and copy the values for:
   - `_otwarchive_session`
   - `user_credentials` (usually just `1`)

> ⚠️ Cookies expire after some time. If the scraper returns no results, log in again and grab fresh ones.

### Fill in `config.py`

Open `config.py` and paste your details:

```python
USERNAME = "your_ao3_username"

COOKIES = {
    "_otwarchive_session": "PASTE_VALUE_HERE",
    "user_credentials": "1",
}
```

---

## Running

```bash
python main.py
```

The script automatically detects how many pages your reading history has and scrapes all of them. Depending on how much you've read, this can take a few minutes. It intentionally pauses between requests to be respectful to AO3's servers.

### Cache

After the first run, your scraped data is saved locally as a `.json` file. The next time you run the script, it will ask whether you want to use the cached data or scrape everything fresh. Using the cache is much faster if you just want to see your stats again.

---

## Folder structure

```
ao3-wrapped/
├── config.py      # your username and cookies (never share this file)
├── scraper.py     # fetches and parses your AO3 reading history
├── stats.py       # computes all statistics
├── main.py        # entry point — run this
└── README.md
```

---

## Privacy

Your cookies and reading data never leave your machine. Everything runs locally — nothing is sent anywhere.

**Never share your `config.py`** or your `_otwarchive_session` cookie with anyone. These grant access to your AO3 account.

---

## Notes

- AO3's reading history only tracks works you visited while logged in.
- Works that have been deleted or orphaned may appear with incomplete info.
- The `REQUEST_DELAY` in `config.py` controls how long the scraper waits between pages. Please don't set it below `1.0` — be kind to AO3's servers.
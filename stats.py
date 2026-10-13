from collections import Counter
from itertools import combinations
 
 
def compute_stats(works: list[dict]) -> dict:
    if not works:
        return {}
 
    total_works = len(works)
    total_words = sum(w["word_count"] for w in works)
 
    ship_counter        = Counter()
    friendship_counter  = Counter()
    fandom_counter      = Counter()
    tag_counter         = Counter()
    author_counter      = Counter()
    author_words        = Counter()
    language_counter    = Counter()
    rating_counter      = Counter()
    complete_counter    = Counter()
    combo_counter       = Counter()
    by_year             = Counter()
    by_month_year       = Counter()
 
    for w in works:
        for s in w["ships"]:
            ship_counter[s] += 1
        for f in w["friendships"]:
            friendship_counter[f] += 1
        for fandom in w["fandoms"]:
            fandom_counter[fandom] += 1
 
        tags = w["freeforms"]
        for tag in tags:
            tag_counter[tag] += 1
 
        if len(tags) >= 2:
            for pair in combinations(sorted(tags), 2):
                combo_counter[pair] += 1
 
        author_counter[w["author"]] += 1
        author_words[w["author"]] += w["word_count"]
 
        lang = w.get("language", "").strip() or "Unknown"
        language_counter[lang] += 1
 
        rating = w.get("rating", "").strip()
        if rating:
            rating_counter[rating] += 1
 
        complete = w.get("complete", "").strip()
        if complete:
            complete_counter[complete] += 1
 
        date = w.get("last_visited", "")
        if date:
            parts = date.split()
            if len(parts) >= 3:
                by_year[parts[2]] += 1
                by_month_year[f"{parts[1]} {parts[2]}"] += 1
 
    most_visited = sorted(works, key=lambda w: w["visits"], reverse=True)[:10]
    longest      = sorted(works, key=lambda w: w["word_count"], reverse=True)[:10]
    shortest     = [w for w in works if w["word_count"] > 0]
    shortest     = sorted(shortest, key=lambda w: w["word_count"])[:5]
 
    multi_visit  = [w for w in works if w["visits"] > 1]
    reread_pct   = round(len(multi_visit) / total_works * 100, 1) if total_works else 0
 
    avg_words    = total_words / total_works if total_works else 0
 
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    def month_key(my: str):
        parts = my.split()
        if len(parts) == 2:
            m, y = parts
            mi = month_order.index(m) if m in month_order else 0
            return (int(y), mi)
        return (0, 0)
 
    sorted_months = sorted(by_month_year.items(), key=lambda x: month_key(x[0]))
 
    return {
        "total_works":          total_works,
        "total_words":          total_words,
        "avg_words_per_fic":    int(avg_words),
        "avg_reading_minutes":  round(avg_words / 250, 1),
        "reread_count":         len(multi_visit),
        "reread_pct":           reread_pct,
        "top_ships":            ship_counter.most_common(10),
        "top_friendships":      friendship_counter.most_common(10),
        "top_fandoms":          fandom_counter.most_common(10),
        "top_tags":             tag_counter.most_common(20),
        "top_tag_combos":       combo_counter.most_common(10),
        "top_authors":          author_counter.most_common(10),
        "top_authors_by_words": author_words.most_common(10),
        "top_languages":        language_counter.most_common(10),
        "rating_breakdown":     rating_counter.most_common(),
        "complete_breakdown":   complete_counter.most_common(),
        "most_visited":         most_visited,
        "longest_fics":         longest,
        "shortest_fics":        shortest,
        "reads_by_year":        sorted(by_year.items()),
        "reads_by_month":       sorted_months,
    }
import json
import os
from rich.console import Console
from rich.table import Table
from rich import box
from scraper import scrape_all_history
from stats import compute_stats
from config import USERNAME
 
console = Console()
CACHE_FILE = f"{USERNAME}_history.json"
 
 
def fmt(n: int) -> str:
    return f"{n:,}"
 
 
def print_table(title, rows, col1, col2_label="Count", truncate=50):
    if not rows:
        return
    t = Table(title=title, box=box.ROUNDED, title_style="bold magenta")
    t.add_column("#", style="dim", width=4)
    t.add_column(col1, style="cyan", max_width=truncate)
    t.add_column(col2_label, style="green", justify="right")
    for i, (name, count) in enumerate(rows, 1):
        t.add_row(str(i), str(name), fmt(count))
    console.print(t)
    console.print()
 
 
def print_fic_table(title, works, value_key, value_label):
    if not works:
        return
    t = Table(title=title, box=box.ROUNDED, title_style="bold magenta")
    t.add_column("#", style="dim", width=4)
    t.add_column("Title", style="cyan", max_width=45)
    t.add_column("Author", style="yellow", max_width=22)
    t.add_column(value_label, style="green", justify="right")
    for i, w in enumerate(works, 1):
        val = fmt(w[value_key])
        t.add_row(str(i), w["title"], w["author"], val)
    console.print(t)
    console.print()
 
 
def load_cache() -> list[dict] | None:
    if os.path.exists(CACHE_FILE):
        console.print(f"[yellow]Cache found:[/yellow] {CACHE_FILE}")
        choice = input("  Use cached data? (y = yes, n = re-scrape): ").strip().lower()
        if choice == "y":
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            console.print(f"[green]Loaded {len(data):,} works from cache.[/green]\n")
            return data
    return None
 
 
def save_cache(works: list[dict]):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(works, f, ensure_ascii=False, indent=2)
    console.print(f"[dim]Cache saved to {CACHE_FILE}[/dim]")
 
 
def main():
    console.rule("[bold magenta]AO3 Reading History Stats[/bold magenta]")
    console.print()
 
    works = load_cache()
    if works is None:
        works = scrape_all_history()
        if not works:
            console.print("[red]No works found. Check username and cookies in config.py[/red]")
            return
        save_cache(works)
 
    stats = compute_stats(works)
 
    console.rule("[bold]📊 Overview[/bold]")
    console.print(f"  Total works read:         [green]{fmt(stats['total_works'])}[/green]")
    console.print(f"  Total words read:         [green]{fmt(stats['total_words'])}[/green]")
    console.print(f"  Avg words per fic:        [green]{fmt(stats['avg_words_per_fic'])}[/green]")
    console.print(f"  Avg reading time/fic:     [green]{stats['avg_reading_minutes']} min[/green] (at 250 wpm)")
    console.print(f"  Fics read more than once: [green]{fmt(stats['reread_count'])}[/green] ({stats['reread_pct']}%)")
    console.print()
 
    if stats["reads_by_year"]:
        console.rule("[bold]📅 Reads by Year[/bold]")
        for year, count in stats["reads_by_year"]:
            console.print(f"  {year}: [green]{fmt(count)}[/green] works")
        console.print()
 
    console.rule("[bold]🌐 Languages[/bold]")
    print_table("Languages Read", stats["top_languages"], "Language")
 
    console.rule("[bold]⭐ Ratings[/bold]")
    print_table("Rating Breakdown", stats["rating_breakdown"], "Rating")
 
    console.rule("[bold]💞 Ships & Friendships[/bold]")
    print_table("Top 10 Ships (/) Read", stats["top_ships"], "Ship")
    print_table("Top 10 Friendships (&) Read", stats["top_friendships"], "Friendship")
 
    console.rule("[bold]🌍 Fandoms[/bold]")
    print_table("Top 10 Fandoms Read", stats["top_fandoms"], "Fandom")
 
    console.rule("[bold]🏷️  Tags[/bold]")
    print_table("Top 20 Tags Read", stats["top_tags"], "Tag")
 
    console.rule("[bold]🔗 Tag Combos[/bold]")
    combo_rows = [(f"{a}  +  {b}", c) for (a, b), c in stats["top_tag_combos"]]
    print_table("Top 10 Tag Combinations", combo_rows, "Tag Pair", truncate=70)
 
    console.rule("[bold]✍️  Authors[/bold]")
    print_table("Top 10 Authors (by fic count)", stats["top_authors"], "Author")
    print_table("Top 10 Authors (by words read)", stats["top_authors_by_words"], "Author", "Words")
 
    console.rule("[bold]📚 Fics[/bold]")
    print_fic_table("Top 10 Longest Fics", stats["longest_fics"], "word_count", "Words")
    print_fic_table("Top 10 Most Visited Fics", stats["most_visited"], "visits", "Visits")
 
    console.rule("[bold magenta]Done![/bold magenta]")
 
 
if __name__ == "__main__":
    main()
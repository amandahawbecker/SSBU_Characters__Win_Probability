# SmashDataCollector3.py
# This code scrape https://ultimateframedata.com/stats into wide and long CSVs.
# Do the following:
#   pip install beautifulsoup4 or (bs4)
#   pip install lxml
#   pip install pandas
#   python ufd_stats_scraper.py

import re
import unicodedata
import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://ultimateframedata.com/stats"

# Alias map to normalize tricky names for later joins (Need to add more to this) 
ALIASES = {
    "r.o.b": "ROB", "rob": "ROB", "r o b": "ROB",
    "mr game & watch": "Mr. Game & Watch", "mr game and watch": "Mr. Game & Watch",
    "dr mario": "Dr. Mario", "dr. mario": "Dr. Mario",
    "pyra/mythra": "Pyra & Mythra", "mythra": "Mythra", "pyra": "Pyra",
    "pokemon trainer": "Pokémon Trainer", "pt": "Pokémon Trainer",
    "banjo & kazooie": "Banjo & Kazooie",
    "king k. rool": "King K. Rool", "k rool": "King K. Rool",
    "ice climbers": "Ice Climbers",
}

def canonize_name(name: str) -> str:
    s = unicodedata.normalize("NFKC", str(name or "").strip())
    s = s.replace("’", "'")
    s = s.replace(".", "")
    s = re.sub(r"\s+", " ", s)
    key = s.lower()
    return ALIASES.get(key, s)

def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; UFD-Stats-Scraper/1.0; +https://ultimateframedata.com/)"
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

def parse_stats_tables(html: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    merged = None

    # Consider headings where the page places section titles
    for hdr in soup.find_all(["h1", "h2", "h3", "h4"]):
        title = hdr.get_text(strip=True)
        # Skip non-sections
        if not title or title.lower() == "stats" or "Back to Home" in title:
            continue
        # Get the next <table> after the heading
        table = hdr.find_next("table")
        if table is None:
            continue

        try:
            df = pd.read_html(str(table))[0]
        except ValueError:
            continue

        # Find the character column (The header varies across tables but contains "character")
        char_col = None
        for c in df.columns:
            if re.search(r"character", str(c), re.I):
                char_col = c
                break
        if char_col is None:
            # No character column → skip
            continue

        # Standardize column names
        df = df.rename(columns={char_col: "Character"})
        df.columns = [re.sub(r"\s*↓", "", str(c)).strip() for c in df.columns]
        # Drop all-NaN columns (sometimes parsing leaves empty cols)
        df = df.dropna(axis=1, how="all")

        # Remove obvious rank columns if present
        for rank_like in ["Rank", "Placement", "#"]:
            if rank_like in df.columns:
                df = df.drop(columns=[rank_like])

        # Prefix non-Character columns with section title to avoid collisions
        prefixed = {}
        for c in df.columns:
            if c == "Character":
                prefixed[c] = c
            else:
                prefixed[c] = f"{title}__{c}"
        df = df.rename(columns=prefixed)

        # Clean character names and build a merge key
        df["character_key"] = df["Character"].map(canonize_name)

        merged = df if merged is None else merged.merge(df, on=["character_key", "Character"], how="outer")

    if merged is None or merged.empty:
        raise RuntimeError("No tables parsed from UFD Stats page.")

    # Coerce all numeric-looking columns (except Character fields)
    for c in merged.columns:
        if c not in ("character_key", "Character"):
            merged[c] = pd.to_numeric(merged[c], errors="coerce")

    # Ensure one row per character_key (keep the first display name seen)
    merged = (merged
              .sort_values(["character_key"])
              .groupby("character_key", as_index=False)
              .first())

    # Reorder columns: key, Character, then metrics
    metric_cols = [c for c in merged.columns if c not in ("character_key", "Character")]
    merged = merged[["character_key", "Character"] + metric_cols]
    return merged

def to_long(df_wide: pd.DataFrame) -> pd.DataFrame:
    metric_cols = [c for c in df_wide.columns if c not in ("character_key", "Character")]
    long = df_wide.melt(id_vars=["character_key", "Character"],
                        value_vars=metric_cols,
                        var_name="metric",
                        value_name="value")
    
    # Split "Section__Metric" into two columns
    section, metric = [], []
    for m in long["metric"]:
        if "__" in m:
            s, k = m.split("__", 1)
        else:
            s, k = "Misc", m
        section.append(s)
        metric.append(k)
    long["section"] = section
    long["stat"] = metric
    # Clean ordering
    long = long[["character_key", "Character", "section", "stat", "value"]].sort_values(
        ["Character", "section", "stat"], ignore_index=True
    )
    return long

def main():
    html = fetch_html(URL)
    wide = parse_stats_tables(html)
    long = to_long(wide)

    wide.to_csv("ufd_stats_wide.csv", index=False)
    long.to_csv("ufd_stats_long.csv", index=False)
    print("Saved ufd_stats_wide.csv and ufd_stats_long.csv")

if __name__ == "__main__":
    main()

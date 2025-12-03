"""
Build character matchup dataset from tournament data
"""
import sqlite3
import pandas as pd
import json
from collections import defaultdict

print("=" * 70)
print("BUILDING MATCHUP DATASET")
print("=" * 70)

conn = sqlite3.connect('ultimate_player_database/ultimate_player_database.db')

# Step 1: Get all players with their character usage
print("\n1. Loading player character data...")
players_query = """
    SELECT player_id, characters
    FROM players
    WHERE game = 'ultimate' 
      AND characters IS NOT NULL 
      AND characters != ''
      AND characters != '{}'
"""

players_df = pd.read_sql_query(players_query, conn)
print(f"   Loaded {len(players_df)} players with character data")

# Parse character data and get primary characters for each player
def get_primary_characters(char_string, top_n=3):
    """Extract top N most used characters for a player"""
    try:
        chars = json.loads(char_string)
        if not chars:
            return []
        
        # Sort by usage count (descending)
        sorted_chars = sorted(chars.items(), key=lambda x: x[1], reverse=True)
        
        # Extract character names (remove 'ultimate/' prefix)
        primary = []
        for char_key, count in sorted_chars[:top_n]:
            char_name = char_key.replace('ultimate/', '').strip()
            if char_name and char_name != 'random':
                primary.append(char_name.lower())
        
        return primary
    except:
        return []

# Create player -> characters mapping
player_chars = {}
for _, row in players_df.iterrows():
    player_id = row['player_id']
    primary_chars = get_primary_characters(row['characters'])
    if primary_chars:
        player_chars[player_id] = primary_chars

print(f"   {len(player_chars)} players with valid character data")

# Step 2: Get tournament sets
print("\n2. Loading tournament sets...")
# Get a sample first to test
sets_query = """
    SELECT key, tournament_key, winner_id, p1_id, p2_id, p1_score, p2_score
    FROM sets
    WHERE game = 'ultimate'
      AND winner_id IS NOT NULL
      AND p1_id IS NOT NULL
      AND p2_id IS NOT NULL
      AND winner_id IN (p1_id, p2_id)
    LIMIT 100000
"""

sets_df = pd.read_sql_query(sets_query, conn)
print(f"   Loaded {len(sets_df)} sets")

# Step 3: Build matchup pairs
print("\n3. Building matchup pairs...")
matchups = []  # List of (char1, char2, winner_is_p1, ...)

def normalize_character_name(char_name):
    """Normalize character names to match smash.csv"""
    char_map = {
        'pokemontrainer': 'pokemon trainer',
        'pyra': 'pyra mythra',
        'pyramythra': 'pyra mythra',
        'mii brawler': 'mii brawler',
        'mii swordfighter': 'mii swordfighter',
        'mii gunner': 'mii gunner',
        'mr game & watch': 'mr. game & watch',
        'gamewatch': 'mr. game & watch',
        'dr mario': 'dr. mario',
        'mariod': 'dr. mario',
        'toonlink': 'toon link',
        'younglink': 'young link',
        'wiifittrainer': 'wii fit trainer',
        'king k rool': 'king k. rool',
        'kingkr': 'king k. rool',
        'kingdedede': 'king dedede',
        'banjokazooie': 'banjo & kazooie',
        'diddykong': 'diddy kong',
        'iceclimbers': 'ice climbers',
        'rosalina': 'rosalina & luma',
        'piranhaplant': 'piranha plant',
        'zero suitsamus': 'zero suit samus',
        'zerosuitsamus': 'zero suit samus',
        'ridley': 'ridley',
    }
    
    char_name = char_name.lower().strip()
    # Remove 'ultimate/' prefix if present
    char_name = char_name.replace('ultimate/', '')
    
    # Check direct mapping
    if char_name in char_map:
        return char_map[char_name]
    
    # Try to match by removing spaces/special chars
    for key, value in char_map.items():
        if key.replace(' ', '').replace('.', '').replace('&', '') == char_name.replace(' ', '').replace('.', '').replace('&', ''):
            return value
    
    # Return as-is (will need manual matching later)
    return char_name

matchup_counts = defaultdict(lambda: {'p1_wins': 0, 'p2_wins': 0})

for _, row in sets_df.iterrows():
    winner_id = str(row['winner_id'])
    p1_id = str(row['p1_id'])
    p2_id = str(row['p2_id'])
    
    # Skip if players not in our character database
    if p1_id not in player_chars or p2_id not in player_chars:
        continue
    
    # Get primary characters for each player
    p1_chars = player_chars[p1_id]
    p2_chars = player_chars[p2_id]
    
    # For now, use most-used character (could improve this logic)
    if not p1_chars or not p2_chars:
        continue
    
    char1 = normalize_character_name(p1_chars[0])
    char2 = normalize_character_name(p2_chars[0])
    
    # Determine winner
    winner_is_p1 = (winner_id == p1_id)
    
    # Create matchup key (alphabetically sorted to avoid duplicates)
    matchup_key = tuple(sorted([char1, char2]))
    
    if winner_is_p1:
        matchup_counts[matchup_key]['p1_wins'] += 1
    else:
        matchup_counts[matchup_key]['p2_wins'] += 1

print(f"\n4. Found {len(matchup_counts)} unique matchup pairs")

# Convert to dataframe
matchup_data = []
for (char1, char2), counts in matchup_counts.items():
    total_games = counts['p1_wins'] + counts['p2_wins']
    if total_games >= 5:  # Only keep matchups with at least 5 games
        matchup_data.append({
            'character_1': char1,
            'character_2': char2,
            'char1_wins': counts['p1_wins'] if char1 < char2 else counts['p2_wins'],
            'char2_wins': counts['p2_wins'] if char1 < char2 else counts['p1_wins'],
            'total_games': total_games,
            'char1_winrate': counts['p1_wins'] / total_games if char1 < char2 else counts['p2_wins'] / total_games
        })

matchups_df = pd.DataFrame(matchup_data)
print(f"   {len(matchups_df)} matchups with >= 5 games")

# Save to CSV
matchups_df.to_csv('character_matchups.csv', index=False)
print(f"\n5. Saved matchup data to 'character_matchups.csv'")

# Show sample
print("\n6. Sample matchup data:")
print(matchups_df.head(20))

conn.close()
print("\n" + "=" * 70)
print("DATASET BUILDING COMPLETE")
print("=" * 70)


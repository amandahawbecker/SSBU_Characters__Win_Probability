"""
Enhanced classifier with technical parameters from ultimate_param.csv
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("BUILDING ENHANCED CLASSIFIER WITH TECHNICAL PARAMETERS")
print("=" * 70)

# 1. Load data
print("\n1. Loading data...")
matchups_df = pd.read_csv('character_matchups.csv')
char_attrs = pd.read_csv('smash.csv')
tech_params = pd.read_csv('ultimate_param.csv', skiprows=2)

print(f"   Matchups: {len(matchups_df)}")
print(f"   Character attributes: {len(char_attrs)}")
print(f"   Technical parameters: {len(tech_params)}")

# Clean technical params - remove unnamed columns
tech_params = tech_params.loc[:, ~tech_params.columns.str.startswith('Unnamed')]

# 2. Normalize character names
print("\n2. Normalizing character names...")
name_variations = {
    'metaknight': 'Meta Knight',
    'littlemac': 'Little Mac',
    'pokemon trainer': 'Pokemon Trainer',
    'king k. rool': 'King K. Rool',
    'king dedede': 'King Dedede',
    'diddy kong': 'Diddy Kong',
    'young link': 'Young Link',
    'toon link': 'Toon Link',
    'dr. mario': 'Dr. Mario',
    'mr. game & watch': 'Mr. Game & Watch',
    'zero suit samus': 'Zero Suit Samus',
    'wii fit trainer': 'Wii Fit Trainer',
    'rosalina & luma': 'Rosalina & Luma',
    'banjo & kazooie': 'Banjo & Kazooie',
    'piranha plant': 'Piranha Plant',
    'pyra mythra': 'Pyra Mythra',
    'mii brawler': 'Mii Brawler',
    'mii swordfighter': 'Mii Swordfighter',
    'mii gunner': 'Mii Gunner',
    'ice climbers': 'Ice Climbers'
}

def normalize_char_name(matchup_name):
    matchup_name = matchup_name.lower().strip()
    if matchup_name in name_variations:
        return name_variations[matchup_name]
    for smash_name in char_attrs['name']:
        if smash_name.lower() == matchup_name:
            return smash_name
    return matchup_name.title()

# Normalize technical params character names
tech_params['char_normalized'] = tech_params['Description'].apply(normalize_char_name)

# Key technical parameters to extract
tech_features = [
    'Weight', 'Gravity', 'Run Maximum Velocity', 'Walk Maximum Velocity',
    'Maximum Horizontal Air Speed', 'Maximum Fall Speed', 'Dash Initial Velocity',
    'Maximum Air Acceleration'
]

print(f"\n3. Extracting technical parameters...")
print(f"   Looking for: {tech_features}")

# Find which columns exist
available_tech_features = []
for feat in tech_features:
    matching_cols = [col for col in tech_params.columns if feat.lower() in col.lower()]
    if matching_cols:
        available_tech_features.append(matching_cols[0])
        print(f"   Found: {matching_cols[0]}")

# 4. Merge matchup data with character attributes
print("\n4. Merging character attributes...")
matchups_df['char1_normalized'] = matchups_df['character_1'].apply(normalize_char_name)
matchups_df['char2_normalized'] = matchups_df['character_2'].apply(normalize_char_name)

char1_attrs = char_attrs.add_suffix('_char1')
char1_attrs = char1_attrs.rename(columns={'name_char1': 'char1_normalized'})
char2_attrs = char_attrs.add_suffix('_char2')
char2_attrs = char2_attrs.rename(columns={'name_char2': 'char2_normalized'})

matchups_with_attrs = matchups_df.merge(
    char1_attrs, on='char1_normalized', how='inner'
).merge(
    char2_attrs, on='char2_normalized', how='inner'
)

# 5. Merge technical parameters
print("\n5. Merging technical parameters...")
tech_params_char1 = tech_params[['char_normalized'] + available_tech_features].copy()
tech_params_char1 = tech_params_char1.add_suffix('_char1')
tech_params_char1 = tech_params_char1.rename(columns={'char_normalized_char1': 'char1_normalized'})

tech_params_char2 = tech_params[['char_normalized'] + available_tech_features].copy()
tech_params_char2 = tech_params_char2.add_suffix('_char2')
tech_params_char2 = tech_params_char2.rename(columns={'char_normalized_char2': 'char2_normalized'})

# Convert technical params to numeric
for col in available_tech_features:
    if f"{col}_char1" in tech_params_char1.columns:
        tech_params_char1[f"{col}_char1"] = pd.to_numeric(tech_params_char1[f"{col}_char1"], errors='coerce')
    if f"{col}_char2" in tech_params_char2.columns:
        tech_params_char2[f"{col}_char2"] = pd.to_numeric(tech_params_char2[f"{col}_char2"], errors='coerce')

matchups_enhanced = matchups_with_attrs.merge(
    tech_params_char1, on='char1_normalized', how='left'
).merge(
    tech_params_char2, on='char2_normalized', how='left'
)

print(f"   Matchups with all data: {len(matchups_enhanced)}")

# 6. Create feature differences
print("\n6. Creating feature differences...")

# Character attribute differences
attributes = ['weight', 'recovery', 'speed', 'combo_game', 'projectiles', 
              'killpower', 'ledgetrap', 'edgeguard', 'spacing', 'cheese']

all_features = []

# Attribute differences
for attr in attributes:
    char1_col = f"{attr}_char1"
    char2_col = f"{attr}_char2"
    if char1_col in matchups_enhanced.columns and char2_col in matchups_enhanced.columns:
        matchups_enhanced[f"{attr}_diff"] = (
            matchups_enhanced[char1_col] - matchups_enhanced[char2_col]
        )
        all_features.append(f"{attr}_diff")

# Technical parameter differences
for tech_feat in available_tech_features:
    char1_col = f"{tech_feat}_char1"
    char2_col = f"{tech_feat}_char2"
    if char1_col in matchups_enhanced.columns and char2_col in matchups_enhanced.columns:
        matchups_enhanced[f"{tech_feat}_diff"] = (
            pd.to_numeric(matchups_enhanced[char1_col], errors='coerce') - 
            pd.to_numeric(matchups_enhanced[char2_col], errors='coerce')
        )
        all_features.append(f"{tech_feat}_diff")

print(f"   Total features: {len(all_features)}")
print(f"   Attribute features: {len(attributes)}")
print(f"   Technical features: {len(all_features) - len(attributes)}")

# 7. Create classification labels
print("\n7. Creating classification labels...")
def classify_matchup_binary(winrate):
    if winrate >= 0.50:
        return 'Char1_Wins'
    else:
        return 'Char2_Wins'

matchups_enhanced['matchup_binary'] = matchups_enhanced['char1_winrate'].apply(classify_matchup_binary)

# 8. Prepare training data
print("\n8. Preparing training data...")
X = matchups_enhanced[all_features].copy()
y = matchups_enhanced['matchup_binary'].copy()

# Remove rows with too many missing values
valid_mask = ~(X.isnull().all(axis=1) | y.isnull())
X = X[valid_mask]
y = y[valid_mask]

# Fill remaining NaN with 0 (for missing technical params)
X = X.fillna(0)

print(f"   Final dataset: {len(X)} matchups")
print(f"   Features: {len(all_features)}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 9. Train enhanced model
print("\n9. Training enhanced model...")
rf_enhanced = RandomForestClassifier(
    n_estimators=100, 
    max_depth=10, 
    random_state=42, 
    n_jobs=-1,
    class_weight='balanced'
)
rf_enhanced.fit(X_train, y_train)
rf_enhanced_pred = rf_enhanced.predict(X_test)

# 10. Evaluate
print("\n10. Evaluating enhanced model...")
accuracy = accuracy_score(y_test, rf_enhanced_pred)
print(f"\nEnhanced Model Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print("\nClassification Report:")
print(classification_report(y_test, rf_enhanced_pred))

# 11. Feature importance
print("\n11. Feature Importance:")
feature_importance = pd.DataFrame({
    'feature': all_features,
    'importance': rf_enhanced.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 15 Most Important Features:")
print(feature_importance.head(15).to_string(index=False))

# Save results
matchups_enhanced.to_csv('matchups_enhanced.csv', index=False)
feature_importance.to_csv('feature_importance_enhanced.csv', index=False)

print("\n" + "=" * 70)
print("ENHANCED MODEL COMPLETE!")
print("=" * 70)
print(f"\nAccuracy: {accuracy*100:.2f}%")
print(f"Features: {len(all_features)} (including {len(all_features) - len(attributes)} technical params)")
print("\nSaved files:")
print("  - matchups_enhanced.csv")
print("  - feature_importance_enhanced.csv")


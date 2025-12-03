"""
Build and train matchup prediction model
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("BUILDING MATCHUP PREDICTION MODEL")
print("=" * 70)

# 1. Load data
print("\n1. Loading data...")
matchups_df = pd.read_csv('character_matchups.csv')
char_attrs = pd.read_csv('smash.csv')

print(f"   Matchups: {len(matchups_df)}")
print(f"   Characters: {len(char_attrs)}")

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
    """Convert matchup character name to match smash.csv format"""
    matchup_name = matchup_name.lower().strip()
    
    if matchup_name in name_variations:
        return name_variations[matchup_name]
    
    for smash_name in char_attrs['name']:
        if smash_name.lower() == matchup_name:
            return smash_name
    
    return matchup_name.title()

matchups_df['char1_normalized'] = matchups_df['character_1'].apply(normalize_char_name)
matchups_df['char2_normalized'] = matchups_df['character_2'].apply(normalize_char_name)

# 3. Merge with character attributes
print("\n3. Merging with character attributes...")
char1_attrs = char_attrs.add_suffix('_char1')
char1_attrs = char1_attrs.rename(columns={'name_char1': 'char1_normalized'})

char2_attrs = char_attrs.add_suffix('_char2')
char2_attrs = char2_attrs.rename(columns={'name_char2': 'char2_normalized'})

matchups_with_attrs = matchups_df.merge(
    char1_attrs, on='char1_normalized', how='inner'
).merge(
    char2_attrs, on='char2_normalized', how='inner'
)

print(f"   Matchups with attributes: {len(matchups_with_attrs)}")

# 4. Create feature differences
print("\n4. Creating feature differences...")
attributes = ['weight', 'recovery', 'speed', 'combo_game', 'projectiles', 
              'killpower', 'ledgetrap', 'edgeguard', 'spacing', 'cheese']

feature_data = []
for attr in attributes:
    char1_col = f"{attr}_char1"
    char2_col = f"{attr}_char2"
    
    if char1_col in matchups_with_attrs.columns and char2_col in matchups_with_attrs.columns:
        matchups_with_attrs[f"{attr}_diff"] = (
            matchups_with_attrs[char1_col] - matchups_with_attrs[char2_col]
        )
        feature_data.append(f"{attr}_diff")

print(f"   Created {len(feature_data)} features")

# 5. Prepare training data
print("\n5. Preparing training data...")
X = matchups_with_attrs[feature_data].copy()
y = matchups_with_attrs['char1_winrate'].copy()

valid_mask = ~(X.isnull().any(axis=1) | y.isnull())
X = X[valid_mask]
y = y[valid_mask]

print(f"   Final dataset: {len(X)} matchups")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"   Training: {len(X_train)}, Test: {len(X_test)}")

# 6. Train models
print("\n6. Training models...")

# Linear Regression
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)
lr_pred = lr_model.predict(X_test)

# Random Forest
rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)

# Gradient Boosting
gb_model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
gb_model.fit(X_train, y_train)
gb_pred = gb_model.predict(X_test)

print("   Models trained!")

# 7. Evaluate models
print("\n7. Evaluating models...")

def evaluate_model(y_true, y_pred, model_name):
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    print(f"\n{model_name}:")
    print(f"  R² Score: {r2:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  MAE: {mae:.4f}")
    
    return {'model': model_name, 'r2': r2, 'rmse': rmse, 'mae': mae}

results = []
results.append(evaluate_model(y_test, lr_pred, "Linear Regression"))
results.append(evaluate_model(y_test, rf_pred, "Random Forest"))
results.append(evaluate_model(y_test, gb_pred, "Gradient Boosting"))

results_df = pd.DataFrame(results)
print("\n" + "=" * 70)

# 8. Feature importance
print("\n8. Feature Importance (Random Forest):")
feature_importance = pd.DataFrame({
    'feature': feature_data,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 Most Important Features:")
print(feature_importance.head(10).to_string(index=False))

# 9. Save model and results
print("\n9. Saving results...")
matchups_with_attrs.to_csv('matchups_with_attributes.csv', index=False)
results_df.to_csv('model_results.csv', index=False)
feature_importance.to_csv('feature_importance.csv', index=False)

print("   Saved files:")
print("     - matchups_with_attributes.csv")
print("     - model_results.csv")
print("     - feature_importance.csv")

# 10. Example predictions
print("\n10. Example Predictions:")

def predict_matchup(char1_name, char2_name, model=rf_model):
    char1_norm = normalize_char_name(char1_name)
    char2_norm = normalize_char_name(char2_name)
    
    char1_data = char_attrs[char_attrs['name'] == char1_norm]
    char2_data = char_attrs[char_attrs['name'] == char2_norm]
    
    if char1_data.empty or char2_data.empty:
        print(f"   Error: Character not found")
        return None
    
    features = []
    for attr in attributes:
        diff = char1_data[attr].values[0] - char2_data[attr].values[0]
        features.append(diff)
    
    features_array = np.array(features).reshape(1, -1)
    win_rate = model.predict(features_array)[0]
    win_rate = max(0, min(1, win_rate))
    
    print(f"\n   {char1_norm} vs {char2_norm}:")
    print(f"   Predicted win rate for {char1_norm}: {win_rate:.1%}")
    print(f"   Predicted win rate for {char2_norm}: {(1-win_rate):.1%}")
    
    return win_rate

predict_matchup('Mario', 'Fox')
predict_matchup('Pikachu', 'Bowser')
predict_matchup('Sonic', 'Joker')

print("\n" + "=" * 70)
print("MODEL BUILDING COMPLETE!")
print("=" * 70)


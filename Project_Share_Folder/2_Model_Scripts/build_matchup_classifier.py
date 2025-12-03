"""
Build matchup classification model - predicts matchup tiers instead of exact win rates
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("BUILDING MATCHUP CLASSIFICATION MODEL")
print("=" * 70)

# 1. Load data
print("\n1. Loading data...")
matchups_df = pd.read_csv('character_matchups.csv')
char_attrs = pd.read_csv('smash.csv')

print(f"   Matchups: {len(matchups_df)}")
print(f"   Characters: {len(char_attrs)}")

# 2. Normalize character names (same as before)
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

# 5. Create classification labels
print("\n5. Creating classification labels...")

# Option 1: Three-class classification (Advantaged/Even/Disadvantaged)
def classify_matchup_tier(winrate):
    if winrate >= 0.55:  # Character 1 advantaged
        return 'Char1_Advantaged'
    elif winrate <= 0.45:  # Character 2 advantaged
        return 'Char2_Advantaged'
    else:  # Even matchup
        return 'Even'

# Option 2: Binary classification (Char1 wins / Char2 wins)
def classify_matchup_binary(winrate):
    if winrate >= 0.50:
        return 'Char1_Wins'
    else:
        return 'Char2_Wins'

# Create both classification targets
matchups_with_attrs['matchup_tier'] = matchups_with_attrs['char1_winrate'].apply(classify_matchup_tier)
matchups_with_attrs['matchup_binary'] = matchups_with_attrs['char1_winrate'].apply(classify_matchup_binary)

# Show distribution
print("\n   Tier distribution:")
print(matchups_with_attrs['matchup_tier'].value_counts())
print("\n   Binary distribution:")
print(matchups_with_attrs['matchup_binary'].value_counts())

# 6. Prepare training data for both tasks
print("\n6. Preparing training data...")

X = matchups_with_attrs[feature_data].copy()
y_tier = matchups_with_attrs['matchup_tier'].copy()
y_binary = matchups_with_attrs['matchup_binary'].copy()

valid_mask = ~(X.isnull().any(axis=1) | y_tier.isnull() | y_binary.isnull())
X = X[valid_mask]
y_tier = y_tier[valid_mask]
y_binary = y_binary[valid_mask]

print(f"   Final dataset: {len(X)} matchups")

# Split data
X_train, X_test, y_tier_train, y_tier_test, y_binary_train, y_binary_test = train_test_split(
    X, y_tier, y_binary, test_size=0.2, random_state=42, stratify=y_tier
)

print(f"   Training: {len(X_train)}, Test: {len(X_test)}")

# 7. Train models - THREE CLASS CLASSIFICATION
print("\n" + "=" * 70)
print("THREE-CLASS CLASSIFICATION (Advantaged/Even/Disadvantaged)")
print("=" * 70)

print("\n7. Training three-class models...")

# Logistic Regression (multi-class)
lr_tier = LogisticRegression(max_iter=1000, random_state=42, multi_class='multinomial')
lr_tier.fit(X_train, y_tier_train)
lr_tier_pred = lr_tier.predict(X_test)

# Random Forest
rf_tier = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
rf_tier.fit(X_train, y_tier_train)
rf_tier_pred = rf_tier.predict(X_test)

# Gradient Boosting
gb_tier = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
gb_tier.fit(X_train, y_tier_train)
gb_tier_pred = gb_tier.predict(X_test)

# 8. Evaluate three-class models
print("\n8. Evaluating three-class models...")

def evaluate_classifier(y_true, y_pred, model_name):
    accuracy = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred)
    
    print(f"\n{model_name} Results:")
    print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"\n  Classification Report:")
    print(report)
    
    return {'model': model_name, 'accuracy': accuracy}

tier_results = []
tier_results.append(evaluate_classifier(y_tier_test, lr_tier_pred, "Logistic Regression (3-class)"))
tier_results.append(evaluate_classifier(y_tier_test, rf_tier_pred, "Random Forest (3-class)"))
tier_results.append(evaluate_classifier(y_tier_test, gb_tier_pred, "Gradient Boosting (3-class)"))

# Confusion matrix for best model (Random Forest)
print("\n   Confusion Matrix (Random Forest - 3-class):")
cm_tier = confusion_matrix(y_tier_test, rf_tier_pred)
print(cm_tier)
print("\n   Classes:", rf_tier.classes_)

# 9. Train models - BINARY CLASSIFICATION
print("\n" + "=" * 70)
print("BINARY CLASSIFICATION (Char1 Wins / Char2 Wins)")
print("=" * 70)

print("\n9. Training binary models...")

# Split for binary classification
X_train_bin, X_test_bin, y_binary_train_bin, y_binary_test_bin = train_test_split(
    X, y_binary, test_size=0.2, random_state=42, stratify=y_binary
)

# Logistic Regression (binary)
lr_binary = LogisticRegression(max_iter=1000, random_state=42)
lr_binary.fit(X_train_bin, y_binary_train_bin)
lr_binary_pred = lr_binary.predict(X_test_bin)

# Random Forest
rf_binary = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
rf_binary.fit(X_train_bin, y_binary_train_bin)
rf_binary_pred = rf_binary.predict(X_test_bin)

# Gradient Boosting
gb_binary = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
gb_binary.fit(X_train_bin, y_binary_train_bin)
gb_binary_pred = gb_binary.predict(X_test_bin)

# 10. Evaluate binary models
print("\n10. Evaluating binary models...")

binary_results = []
binary_results.append(evaluate_classifier(y_binary_test_bin, lr_binary_pred, "Logistic Regression (binary)"))
binary_results.append(evaluate_classifier(y_binary_test_bin, rf_binary_pred, "Random Forest (binary)"))
binary_results.append(evaluate_classifier(y_binary_test_bin, gb_binary_pred, "Gradient Boosting (binary)"))

# Confusion matrix for best binary model
print("\n   Confusion Matrix (Random Forest - binary):")
cm_binary = confusion_matrix(y_binary_test_bin, rf_binary_pred)
print(cm_binary)
print("\n   Classes:", rf_binary.classes_)

# 11. Feature importance
print("\n" + "=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)

print("\n11. Feature Importance (Random Forest - 3-class):")
feature_importance_tier = pd.DataFrame({
    'feature': feature_data,
    'importance': rf_tier.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 Most Important Features:")
print(feature_importance_tier.head(10).to_string(index=False))

# 12. Save results
print("\n12. Saving results...")
tier_results_df = pd.DataFrame(tier_results)
binary_results_df = pd.DataFrame(binary_results)
feature_importance_tier.to_csv('feature_importance_classifier.csv', index=False)
tier_results_df.to_csv('classifier_tier_results.csv', index=False)
binary_results_df.to_csv('classifier_binary_results.csv', index=False)

print("   Saved files:")
print("     - feature_importance_classifier.csv")
print("     - classifier_tier_results.csv")
print("     - classifier_binary_results.csv")

# 13. Example predictions
print("\n" + "=" * 70)
print("EXAMPLE PREDICTIONS")
print("=" * 70)

def predict_matchup_classifier(char1_name, char2_name, model_tier=rf_tier, model_binary=rf_binary):
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
    
    # Predict tier
    tier_pred = model_tier.predict(features_array)[0]
    tier_proba = model_tier.predict_proba(features_array)[0]
    
    # Predict binary
    binary_pred = model_binary.predict(features_array)[0]
    binary_proba = model_binary.predict_proba(features_array)[0]
    
    print(f"\n   {char1_norm} vs {char2_norm}:")
    print(f"\n   Three-Class Prediction: {tier_pred}")
    print(f"   Probabilities:")
    for class_name, proba in zip(model_tier.classes_, tier_proba):
        print(f"     {class_name}: {proba:.1%}")
    
    print(f"\n   Binary Prediction: {binary_pred}")
    print(f"   Probabilities:")
    for class_name, proba in zip(model_binary.classes_, binary_proba):
        print(f"     {class_name}: {proba:.1%}")
    
    return tier_pred, binary_pred

print("\n13. Example Predictions:")

predict_matchup_classifier('Mario', 'Fox')
print("\n" + "-" * 70)
predict_matchup_classifier('Pikachu', 'Bowser')
print("\n" + "-" * 70)
predict_matchup_classifier('Sonic', 'Joker')

# 14. Summary
print("\n" + "=" * 70)
print("CLASSIFICATION MODEL SUMMARY")
print("=" * 70)

print(f"\nDataset: {len(X)} matchup pairs")
print(f"Features: {len(feature_data)} attribute differences")

print(f"\nThree-Class Classification (Best Model: Random Forest):")
best_tier = max(tier_results, key=lambda x: x['accuracy'])
print(f"  Accuracy: {best_tier['accuracy']:.4f} ({best_tier['accuracy']*100:.2f}%)")
print(f"  Model: {best_tier['model']}")

print(f"\nBinary Classification (Best Model: Random Forest):")
best_binary = max(binary_results, key=lambda x: x['accuracy'])
print(f"  Accuracy: {best_binary['accuracy']:.4f} ({best_binary['accuracy']*100:.2f}%)")
print(f"  Model: {best_binary['model']}")

print("\n" + "=" * 70)
print("CLASSIFICATION MODEL COMPLETE!")
print("=" * 70)


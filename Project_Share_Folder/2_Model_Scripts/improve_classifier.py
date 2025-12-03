"""
Improved classifier with class weights to handle imbalance
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("IMPROVED CLASSIFIER WITH CLASS WEIGHTS")
print("=" * 70)

# Load the merged data
print("\n1. Loading data...")
matchups_with_attrs = pd.read_csv('matchups_with_attributes.csv')

# Recreate classification labels (same as before)
def classify_matchup_tier(winrate):
    if winrate >= 0.55:
        return 'Char1_Advantaged'
    elif winrate <= 0.45:
        return 'Char2_Advantaged'
    else:
        return 'Even'

def classify_matchup_binary(winrate):
    if winrate >= 0.50:
        return 'Char1_Wins'
    else:
        return 'Char2_Wins'

matchups_with_attrs['matchup_tier'] = matchups_with_attrs['char1_winrate'].apply(classify_matchup_tier)
matchups_with_attrs['matchup_binary'] = matchups_with_attrs['char1_winrate'].apply(classify_matchup_binary)

# Features
attributes = ['weight', 'recovery', 'speed', 'combo_game', 'projectiles', 
              'killpower', 'ledgetrap', 'edgeguard', 'spacing', 'cheese']
feature_data = [f"{attr}_diff" for attr in attributes]

# Prepare data
X = matchups_with_attrs[feature_data].copy()
y_tier = matchups_with_attrs['matchup_tier'].copy()
y_binary = matchups_with_attrs['matchup_binary'].copy()

valid_mask = ~(X.isnull().any(axis=1) | y_tier.isnull() | y_binary.isnull())
X = X[valid_mask]
y_tier = y_tier[valid_mask]
y_binary = y_binary[valid_mask]

print(f"   Dataset: {len(X)} matchups")

# Calculate class weights
print("\n2. Calculating class weights...")

class_weights_tier = compute_class_weight('balanced', classes=np.unique(y_tier), y=y_tier)
class_weights_dict_tier = dict(zip(np.unique(y_tier), class_weights_tier))
print(f"   Three-class weights: {class_weights_dict_tier}")

class_weights_binary = compute_class_weight('balanced', classes=np.unique(y_binary), y=y_binary)
class_weights_dict_binary = dict(zip(np.unique(y_binary), class_weights_binary))
print(f"   Binary weights: {class_weights_dict_binary}")

# Split data
X_train_tier, X_test_tier, y_train_tier, y_test_tier = train_test_split(
    X, y_tier, test_size=0.2, random_state=42, stratify=y_tier
)

X_train_bin, X_test_bin, y_train_bin, y_test_bin = train_test_split(
    X, y_binary, test_size=0.2, random_state=42, stratify=y_binary
)

# Train improved models with class weights
print("\n3. Training improved models with class weights...")

# Three-class with balanced weights
rf_tier_improved = RandomForestClassifier(
    n_estimators=100, 
    max_depth=10, 
    random_state=42, 
    n_jobs=-1,
    class_weight='balanced'  # Automatically balance classes
)
rf_tier_improved.fit(X_train_tier, y_train_tier)
rf_tier_improved_pred = rf_tier_improved.predict(X_test_tier)

# Binary with balanced weights
rf_binary_improved = RandomForestClassifier(
    n_estimators=100, 
    max_depth=10, 
    random_state=42, 
    n_jobs=-1,
    class_weight='balanced'
)
rf_binary_improved.fit(X_train_bin, y_train_bin)
rf_binary_improved_pred = rf_binary_improved.predict(X_test_bin)

# Evaluate
print("\n4. Evaluating improved models...")

print("\n" + "=" * 70)
print("IMPROVED THREE-CLASS CLASSIFICATION")
print("=" * 70)

accuracy_tier_improved = accuracy_score(y_test_tier, rf_tier_improved_pred)
print(f"\nAccuracy: {accuracy_tier_improved:.4f} ({accuracy_tier_improved*100:.2f}%)")
print("\nClassification Report:")
print(classification_report(y_test_tier, rf_tier_improved_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test_tier, rf_tier_improved_pred))

print("\n" + "=" * 70)
print("IMPROVED BINARY CLASSIFICATION")
print("=" * 70)

accuracy_binary_improved = accuracy_score(y_test_bin, rf_binary_improved_pred)
print(f"\nAccuracy: {accuracy_binary_improved:.4f} ({accuracy_binary_improved*100:.2f}%)")
print("\nClassification Report:")
print(classification_report(y_test_bin, rf_binary_improved_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test_bin, rf_binary_improved_pred))

print("\n" + "=" * 70)
print("COMPARISON: Before vs After Class Weights")
print("=" * 70)

print("\nThree-Class Classification:")
print(f"  Original (no weights): 73.92%")
print(f"  Improved (balanced):   {accuracy_tier_improved*100:.2f}%")
print(f"  Change:                {accuracy_tier_improved*100 - 73.92:.2f}%")

print("\nBinary Classification:")
print(f"  Original (no weights): 85.48%")
print(f"  Improved (balanced):   {accuracy_binary_improved*100:.2f}%")
print(f"  Change:                {accuracy_binary_improved*100 - 85.48:.2f}%")

print("\n" + "=" * 70)
print("Note: Class weights help balance predictions across all classes,")
print("      even if overall accuracy might slightly decrease.")
print("      The improved model should have better recall for minority classes.")
print("=" * 70)


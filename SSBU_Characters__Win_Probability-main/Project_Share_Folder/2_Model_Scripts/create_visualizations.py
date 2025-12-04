"""
Create comprehensive visualizations for matchup prediction project
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path

def get_data_path(filename, results_dir=False):
    """Find data file in 1_Data_Files, 4_Results, or current directory"""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "1_Data_Files"
    results_path = script_dir.parent / "4_Results"
    
    # Check results directory first if requested
    if results_dir and results_path.exists():
        file_path = results_path / filename
        if file_path.exists():
            return str(file_path)
    
    # Try 1_Data_Files
    if data_dir.exists():
        file_path = data_dir / filename
        if file_path.exists():
            return str(file_path)
    
    # Fallback to current directory
    if Path(filename).exists():
        return filename
    
    # Return the path anyway (will raise error if doesn't exist)
    if results_dir and results_path.exists():
        return str(results_path / filename)
    return str(data_dir / filename) if data_dir.exists() else filename

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

print("=" * 70)
print("CREATING VISUALIZATIONS")
print("=" * 70)

# 1. Load data
print("\n1. Loading data...")
matchups_df = pd.read_csv(get_data_path('character_matchups.csv'))
char_attrs = pd.read_csv(get_data_path('smash.csv'))
try:
    feature_importance = pd.read_csv(get_data_path('feature_importance_enhanced.csv', results_dir=True))
    enhanced = True
except:
    feature_importance = pd.read_csv(get_data_path('feature_importance_classifier.csv', results_dir=True))
    enhanced = False

print(f"   Matchups: {len(matchups_df)}")
print(f"   Features analyzed: {len(feature_importance)}")

# 2. Feature Importance Visualization
print("\n2. Creating feature importance plot...")
plt.figure(figsize=(12, 8))
top_features = feature_importance.head(15).sort_values('importance', ascending=True)
colors = sns.color_palette("viridis", len(top_features))
plt.barh(range(len(top_features)), top_features['importance'], color=colors)
plt.yticks(range(len(top_features)), top_features['feature'].str.replace('_diff', '').str.replace('_', ' ').str.title())
plt.xlabel('Importance', fontsize=12, fontweight='bold')
plt.title('Top 15 Most Important Features for Matchup Prediction', fontsize=14, fontweight='bold')
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=600, bbox_inches='tight')
print("   Saved: feature_importance.png")
plt.close()

# 3. Matchup Win Rate Distribution
print("\n3. Creating win rate distribution plot...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram
axes[0].hist(matchups_df['char1_winrate'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
axes[0].axvline(0.5, color='red', linestyle='--', linewidth=2, label='50% (Even)')
axes[0].set_xlabel('Win Rate', fontweight='bold')
axes[0].set_ylabel('Frequency', fontweight='bold')
axes[0].set_title('Distribution of Matchup Win Rates', fontweight='bold')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Box plot by matchup tier
def get_tier(winrate):
    if winrate >= 0.55:
        return 'Char1 Advantaged'
    elif winrate <= 0.45:
        return 'Char2 Advantaged'
    else:
        return 'Even'

matchups_df['tier'] = matchups_df['char1_winrate'].apply(get_tier)
tier_order = ['Char2 Advantaged', 'Even', 'Char1 Advantaged']
matchups_tier = matchups_df[matchups_df['tier'].isin(tier_order)]

sns.boxplot(data=matchups_tier, y='tier', x='char1_winrate', ax=axes[1], order=tier_order)
axes[1].axvline(0.5, color='red', linestyle='--', linewidth=2)
axes[1].set_xlabel('Win Rate', fontweight='bold')
axes[1].set_ylabel('Matchup Tier', fontweight='bold')
axes[1].set_title('Win Rate Distribution by Matchup Tier', fontweight='bold')
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('winrate_distribution.png', dpi=600, bbox_inches='tight')
print("   Saved: winrate_distribution.png")
plt.close()

# 4. Top Matchups Visualization
print("\n4. Creating top matchups plot...")
# Get most common matchups
top_matchups = matchups_df.nlargest(20, 'total_games')
fig, ax = plt.subplots(figsize=(12, 8))
colors = ['green' if x > 0.55 else 'red' if x < 0.45 else 'gray' for x in top_matchups['char1_winrate']]
matchup_labels = [f"{row['character_1']} vs {row['character_2']}" for _, row in top_matchups.iterrows()]
y_pos = np.arange(len(matchup_labels))
bars = ax.barh(y_pos, top_matchups['char1_winrate'] * 100, color=colors, alpha=0.7)
ax.axvline(50, color='black', linestyle='--', linewidth=2, label='50% (Even)')
ax.set_yticks(y_pos)
ax.set_yticklabels(matchup_labels)
ax.set_xlabel('Win Rate (%)', fontweight='bold')
ax.set_title('Top 20 Most Played Matchups (by game count)', fontweight='bold', fontsize=14)
ax.legend()
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('top_matchups.png', dpi=600, bbox_inches='tight')
print("   Saved: top_matchups.png")
plt.close()

# 5. Character Attribute Comparison
print("\n5. Creating attribute comparison plot...")
# Select a few key attributes to visualize
key_attrs = ['weight', 'speed', 'killpower', 'recovery']
char_sample = char_attrs[['name'] + key_attrs].head(15)  # Top 15 characters

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
for idx, attr in enumerate(key_attrs):
    ax = axes[idx // 2, idx % 2]
    sorted_chars = char_sample.sort_values(attr, ascending=True)
    ax.barh(range(len(sorted_chars)), sorted_chars[attr], color=sns.color_palette("coolwarm", len(sorted_chars)))
    ax.set_yticks(range(len(sorted_chars)))
    ax.set_yticklabels(sorted_chars['name'])
    ax.set_xlabel(attr.title(), fontweight='bold')
    ax.set_title(f'{attr.title()} Distribution (Top 15 Characters)', fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('character_attributes.png', dpi=600, bbox_inches='tight')
print("   Saved: character_attributes.png")
plt.close()

# 6. Matchup Matrix Heatmap (sample)
print("\n6. Creating matchup matrix heatmap...")
# Select top characters by popularity
top_chars = char_attrs.nlargest(15, 'popularity')['name'].tolist()

# Create matchup matrix for top characters
matchup_matrix = pd.DataFrame(index=top_chars, columns=top_chars)
for char1 in top_chars:
    for char2 in top_chars:
        if char1 == char2:
            matchup_matrix.loc[char1, char2] = 0.5  # Even for same character
        else:
            # Find matchup
            matchup = matchups_df[
                ((matchups_df['character_1'] == char1.lower()) & 
                 (matchups_df['character_2'] == char2.lower())) |
                ((matchups_df['character_1'] == char2.lower()) & 
                 (matchups_df['character_2'] == char1.lower()))
            ]
            if len(matchup) > 0:
                row = matchup.iloc[0]
                if row['character_1'] == char1.lower():
                    winrate = row['char1_winrate']
                else:
                    winrate = 1 - row['char1_winrate']
                matchup_matrix.loc[char1, char2] = winrate
            else:
                matchup_matrix.loc[char1, char2] = np.nan

matchup_matrix = matchup_matrix.astype(float)

plt.figure(figsize=(12, 10))
sns.heatmap(matchup_matrix, annot=True, fmt='.2f', cmap='RdYlGn', center=0.5, 
            vmin=0, vmax=1, cbar_kws={'label': 'Win Rate'}, square=True)
plt.title('Matchup Matrix Heatmap (Top 15 Characters by Popularity)', 
          fontweight='bold', fontsize=14, pad=20)
plt.xlabel('Character 2', fontweight='bold')
plt.ylabel('Character 1', fontweight='bold')
plt.tight_layout()
plt.savefig('matchup_matrix_heatmap.png', dpi=600, bbox_inches='tight')
print("   Saved: matchup_matrix_heatmap.png")
plt.close()

# 7. Model Comparison (if we have both models)
print("\n7. Creating model comparison chart...")
try:
    results = pd.read_csv(get_data_path('classifier_binary_results.csv', results_dir=True))
    models = results['model'].tolist()
    accuracies = results['accuracy'].tolist()
    
    plt.figure(figsize=(10, 6))
    colors_comp = sns.color_palette("husl", len(models))
    bars = plt.bar(models, [acc * 100 for acc in accuracies], color=colors_comp, alpha=0.7, edgecolor='black')
    plt.ylabel('Accuracy (%)', fontweight='bold')
    plt.title('Model Performance Comparison (Binary Classification)', fontweight='bold', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{acc*100:.2f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('model_comparison.png', dpi=600, bbox_inches='tight')
    print("   Saved: model_comparison.png")
    plt.close()
except:
    print("   Model comparison data not found, skipping...")

# 8. Feature Type Breakdown
print("\n8. Creating feature type breakdown...")
feature_importance['feature_type'] = feature_importance['feature'].apply(
    lambda x: 'Technical Parameter' if any(tech in x for tech in ['Velocity', 'Speed', 'Gravity', 'Acceleration', 'Dash']) 
    else 'Character Attribute'
)

type_importance = feature_importance.groupby('feature_type')['importance'].sum()

plt.figure(figsize=(8, 6))
colors_pie = sns.color_palette("Set2", len(type_importance))
plt.pie(type_importance.values, labels=type_importance.index, autopct='%1.1f%%', 
        colors=colors_pie, startangle=90, textprops={'fontweight': 'bold'})
plt.title('Feature Importance by Type', fontweight='bold', fontsize=14)
plt.tight_layout()
plt.savefig('feature_type_breakdown.png', dpi=600, bbox_inches='tight')
print("   Saved: feature_type_breakdown.png")
plt.close()

print("\n" + "=" * 70)
print("VISUALIZATIONS COMPLETE!")
print("=" * 70)
print("\nGenerated files:")
print("  1. feature_importance.png")
print("  2. winrate_distribution.png")
print("  3. top_matchups.png")
print("  4. character_attributes.png")
print("  5. matchup_matrix_heatmap.png")
print("  6. model_comparison.png (if available)")
print("  7. feature_type_breakdown.png")


"""
Interactive Matchup Predictor Tool
A user-friendly interface for predicting character matchups
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
import os

class MatchupPredictor:
    def __init__(self):
        """Initialize the predictor with data and model"""
        print("Loading data and building model...")
        self.load_data()
        self.build_model()
        
    def load_data(self):
        """Load all necessary data"""
        from pathlib import Path
        
        # Find data files in 1_Data_Files directory
        current_file = Path(__file__).parent
        project_root = current_file.parent
        data_dir = project_root / "1_Data_Files"
        
        # Build file paths
        smash_path = data_dir / "smash.csv"
        matchups_path = data_dir / "character_matchups.csv"
        
        # Check if files exist, fallback to current directory if needed
        if not smash_path.exists():
            smash_path = Path("smash.csv")
        if not matchups_path.exists():
            matchups_path = Path("character_matchups.csv")
        
        if not smash_path.exists():
            raise FileNotFoundError(f"Could not find smash.csv. Looked in: {data_dir} and current directory")
        if not matchups_path.exists():
            raise FileNotFoundError(f"Could not find character_matchups.csv. Looked in: {data_dir} and current directory")
        
        # Load character data
        self.char_attrs = pd.read_csv(smash_path)
        
        # Load matchup data
        matchups_df = pd.read_csv(matchups_path)
        
        # Normalize names
        name_variations = {
            'metaknight': 'Meta Knight', 'littlemac': 'Little Mac',
            'pokemon trainer': 'Pokemon Trainer', 'king k. rool': 'King K. Rool',
            'king dedede': 'King Dedede', 'diddy kong': 'Diddy Kong',
            'young link': 'Young Link', 'toon link': 'Toon Link',
            'dr. mario': 'Dr. Mario', 'mr. game & watch': 'Mr. Game & Watch',
            'zero suit samus': 'Zero Suit Samus', 'wii fit trainer': 'Wii Fit Trainer',
            'rosalina & luma': 'Rosalina & Luma', 'banjo & kazooie': 'Banjo & Kazooie',
            'piranha plant': 'Piranha Plant', 'pyra mythra': 'Pyra Mythra',
            'mii brawler': 'Mii Brawler', 'mii swordfighter': 'Mii Swordfighter',
            'mii gunner': 'Mii Gunner', 'ice climbers': 'Ice Climbers'
        }
        
        def normalize_char_name(matchup_name):
            matchup_name = matchup_name.lower().strip()
            if matchup_name in name_variations:
                return name_variations[matchup_name]
            for smash_name in self.char_attrs['name']:
                if smash_name.lower() == matchup_name:
                    return smash_name
            return matchup_name.title()
        
        # Merge data
        matchups_df['char1_normalized'] = matchups_df['character_1'].apply(normalize_char_name)
        matchups_df['char2_normalized'] = matchups_df['character_2'].apply(normalize_char_name)
        
        char1_attrs = self.char_attrs.add_suffix('_char1')
        char1_attrs = char1_attrs.rename(columns={'name_char1': 'char1_normalized'})
        char2_attrs = self.char_attrs.add_suffix('_char2')
        char2_attrs = char2_attrs.rename(columns={'name_char2': 'char2_normalized'})
        
        matchups_with_attrs = matchups_df.merge(
            char1_attrs, on='char1_normalized', how='inner'
        ).merge(
            char2_attrs, on='char2_normalized', how='inner'
        )
        
        # Create features
        attributes = ['weight', 'recovery', 'speed', 'combo_game', 'projectiles', 
                      'killpower', 'ledgetrap', 'edgeguard', 'spacing', 'cheese']
        
        self.feature_names = []
        for attr in attributes:
            char1_col = f"{attr}_char1"
            char2_col = f"{attr}_char2"
            if char1_col in matchups_with_attrs.columns:
                matchups_with_attrs[f"{attr}_diff"] = (
                    matchups_with_attrs[char1_col] - matchups_with_attrs[char2_col]
                )
                self.feature_names.append(f"{attr}_diff")
        
        # Create labels
        def classify_binary(winrate):
            return 'Char1_Wins' if winrate >= 0.50 else 'Char2_Wins'
        
        matchups_with_attrs['matchup_binary'] = matchups_with_attrs['char1_winrate'].apply(classify_binary)
        
        # Prepare training data
        X = matchups_with_attrs[self.feature_names].copy()
        y = matchups_with_attrs['matchup_binary'].copy()
        
        valid_mask = ~(X.isnull().any(axis=1) | y.isnull())
        self.X = X[valid_mask]
        self.y = y[valid_mask]
        self.matchups_data = matchups_with_attrs[valid_mask].copy()
        
        self.normalize_char_name = normalize_char_name
        self.attributes = attributes
        
    def build_model(self):
        """Build and train the model"""
        from sklearn.model_selection import train_test_split
        
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42, stratify=self.y
        )
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        self.model.fit(X_train, y_train)
        
        from sklearn.metrics import accuracy_score
        accuracy = accuracy_score(y_test, self.model.predict(X_test))
        print(f"Model trained! Accuracy: {accuracy*100:.2f}%")
        
    def predict(self, char1_name, char2_name):
        """Predict matchup outcome with symmetric predictions (consistent regardless of order)"""
        # Normalize names
        char1_norm = self.normalize_char_name(char1_name)
        char2_norm = self.normalize_char_name(char2_name)
        
        # Get character data
        char1_data = self.char_attrs[self.char_attrs['name'] == char1_norm]
        char2_data = self.char_attrs[self.char_attrs['name'] == char2_norm]
        
        if char1_data.empty:
            return None, f"Character '{char1_name}' not found"
        if char2_data.empty:
            return None, f"Character '{char2_name}' not found"
        
        # SYMMETRIC PREDICTION: Predict both directions and use consensus
        # This ensures same matchup gives same prediction regardless of order
        
        # Direction 1: char1 vs char2
        features1 = []
        for attr in self.attributes:
            diff = char1_data[attr].values[0] - char2_data[attr].values[0]
            features1.append(diff)
        features1_array = np.array(features1).reshape(1, -1)
        
        pred1 = self.model.predict(features1_array)[0]
        prob1 = self.model.predict_proba(features1_array)[0]
        
        # Direction 2: char2 vs char1 (flipped order)
        features2 = []
        for attr in self.attributes:
            diff = char2_data[attr].values[0] - char1_data[attr].values[0]
            features2.append(diff)
        features2_array = np.array(features2).reshape(1, -1)
        
        pred2 = self.model.predict(features2_array)[0]
        prob2 = self.model.predict_proba(features2_array)[0]
        
        # Interpret predictions to get actual winner names
        # Direction 1: char1 vs char2
        if pred1 == 'Char1_Wins':
            winner1 = char1_norm
            prob_win1 = prob1[0]
        else:
            winner1 = char2_norm
            prob_win1 = prob1[1]
        
        # Direction 2: char2 vs char1 (char2 is now character 1 in this direction)
        if pred2 == 'Char1_Wins':
            winner2 = char2_norm  # char2 is character 1 in this direction
            prob_win2 = prob2[0]
        else:
            winner2 = char1_norm  # char1 is character 2 in this direction
            prob_win2 = prob2[1]
        
        # Use consensus: average probabilities for consistent prediction
        if winner1 == winner2:
            # Both directions agree
            final_winner = winner1
            final_prob = (prob_win1 + prob_win2) / 2
        else:
            # Directions disagree - use average probability
            # Calculate average probability for each character
            if winner1 == char1_norm:
                prob_char1_avg = (prob_win1 + (1 - prob_win2)) / 2
                prob_char2_avg = ((1 - prob_win1) + prob_win2) / 2
            else:
                prob_char1_avg = ((1 - prob_win1) + prob_win2) / 2
                prob_char2_avg = (prob_win1 + (1 - prob_win2)) / 2
            
            if prob_char1_avg > prob_char2_avg:
                final_winner = char1_norm
                final_prob = prob_char1_avg
            else:
                final_winner = char2_norm
                final_prob = prob_char2_avg
        
        # Determine final prediction label
        if final_winner == char1_norm:
            final_prediction = 'Char1_Wins'
            char1_prob = final_prob
            char2_prob = 1 - final_prob
        else:
            final_prediction = 'Char2_Wins'
            char1_prob = 1 - final_prob
            char2_prob = final_prob
        
        # Get attribute comparison
        comparison = {}
        for attr in self.attributes:
            comparison[attr] = {
                char1_norm: char1_data[attr].values[0],
                char2_norm: char2_data[attr].values[0],
                'difference': char1_data[attr].values[0] - char2_data[attr].values[0]
            }
        
        result = {
            'char1': char1_norm,
            'char2': char2_norm,
            'prediction': final_prediction,
            'probabilities': {
                'Char1_Wins': char1_prob,
                'Char2_Wins': char2_prob
            },
            'comparison': comparison,
            'predicted_winner': final_winner,
            'confidence': final_prob
        }
        
        return result, None
    
    def get_available_characters(self):
        """Get list of available characters"""
        return sorted(self.char_attrs['name'].tolist())


def print_prediction(result):
    """Print prediction results nicely"""
    print("\n" + "=" * 70)
    print(f"MATCHUP PREDICTION: {result['char1']} vs {result['char2']}")
    print("=" * 70)
    
    # Prediction
    if result['prediction'] == 'Char1_Wins':
        winner = result['char1']
        confidence = result['probabilities']['Char1_Wins']
    else:
        winner = result['char2']
        confidence = result['probabilities']['Char2_Wins']
    
    print(f"\n🏆 PREDICTED WINNER: {winner}")
    print(f"📊 Confidence: {confidence*100:.1f}%")
    
    print(f"\n📈 Win Probabilities:")
    print(f"   {result['char1']}: {result['probabilities'].get('Char1_Wins', 0)*100:.1f}%")
    print(f"   {result['char2']}: {result['probabilities'].get('Char2_Wins', 0)*100:.1f}%")
    
    # Attribute comparison
    print(f"\n⚔️  Attribute Comparison:")
    print(f"   {'Attribute':<20} {result['char1']:<20} {result['char2']:<20} {'Advantage':<15}")
    print("   " + "-" * 75)
    
    for attr, values in result['comparison'].items():
        diff = values['difference']
        if abs(diff) < 0.1:
            advantage = "≈ Even"
        elif diff > 0:
            advantage = f"{result['char1']} +{diff:.1f}"
        else:
            advantage = f"{result['char2']} +{abs(diff):.1f}"
        
        print(f"   {attr.title():<20} {values[result['char1']]:<20.1f} {values[result['char2']]:<20.1f} {advantage:<15}")
    
    print("\n" + "=" * 70)


def interactive_mode():
    """Run interactive command-line interface"""
    predictor = MatchupPredictor()
    characters = predictor.get_available_characters()
    
    print("\n" + "=" * 70)
    print("SUPER SMASH BROS. ULTIMATE - MATCHUP PREDICTOR")
    print("=" * 70)
    print("\nWelcome! This tool predicts matchup outcomes using ML.")
    print("Enter character names to see predictions.\n")
    
    while True:
        print("\nOptions:")
        print("  1. Predict matchup")
        print("  2. List all characters")
        print("  3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            print(f"\nAvailable characters ({len(characters)} total):")
            print(f"Examples: {', '.join(characters[:10])}...")
            
            char1 = input("\nEnter Character 1 name: ").strip()
            char2 = input("Enter Character 2 name: ").strip()
            
            result, error = predictor.predict(char1, char2)
            
            if error:
                print(f"\n❌ Error: {error}")
                print(f"Available characters: {', '.join(characters[:20])}...")
            else:
                print_prediction(result)
        
        elif choice == '2':
            print(f"\nAll {len(characters)} characters:")
            for i, char in enumerate(characters, 1):
                print(f"  {i:3d}. {char}")
        
        elif choice == '3':
            print("\nThanks for using the Matchup Predictor! 🎮")
            break
        
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    interactive_mode()


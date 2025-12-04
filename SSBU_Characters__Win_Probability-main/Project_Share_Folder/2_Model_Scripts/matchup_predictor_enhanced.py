"""
Enhanced Matchup Predictor - Uses enhanced classifier with technical parameters
This is the updated version that should be used instead of the backup
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os
from pathlib import Path

class EnhancedMatchupPredictor:
    def __init__(self, data_dir=None):
        """Initialize the predictor with enhanced features (attributes + technical params)"""
        print("Loading data and building enhanced model...")
        self.data_dir = data_dir
        self.load_data()
        self.build_model()
        
    def load_data(self):
        """Load all necessary data"""
        base_dir = Path(__file__).parent.parent if self.data_dir is None else Path(self.data_dir)
        data_path = base_dir / "1_Data_Files"
        
        # Load character data
        smash_path = data_path / "smash.csv"
        matchups_path = data_path / "character_matchups.csv"
        tech_params_path = data_path / "ultimate_param.csv"
        
        if not smash_path.exists():
            raise FileNotFoundError(f"Could not find smash.csv at {smash_path}")
        if not matchups_path.exists():
            raise FileNotFoundError(f"Could not find character_matchups.csv at {matchups_path}")
        
        self.char_attrs = pd.read_csv(smash_path)
        
        # Load matchup data
        matchups_df = pd.read_csv(matchups_path)
        
        # Try to load technical parameters (optional)
        tech_params = None
        if tech_params_path.exists():
            try:
                tech_params = pd.read_csv(tech_params_path, skiprows=2)
                tech_params = tech_params.loc[:, ~tech_params.columns.str.startswith('Unnamed')]
            except Exception as e:
                print(f"Warning: Could not load technical parameters: {e}")
        
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
        
        self.normalize_char_name = normalize_char_name
        
        # Merge matchup data with character attributes
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
        
        # Try to merge technical parameters if available
        if tech_params is not None:
            try:
                tech_features = [
                    'Weight', 'Gravity', 'Run Maximum Velocity', 'Walk Maximum Velocity',
                    'Maximum Horizontal Air Speed', 'Maximum Fall Speed', 'Dash Initial Velocity',
                    'Maximum Air Acceleration'
                ]
                
                tech_params['char_normalized'] = tech_params['Description'].apply(normalize_char_name)
                
                available_tech_features = []
                for feat in tech_features:
                    matching_cols = [col for col in tech_params.columns if feat.lower() in col.lower()]
                    if matching_cols:
                        available_tech_features.append(matching_cols[0])
                
                if available_tech_features:
                    tech_params_char1 = tech_params[['char_normalized'] + available_tech_features].copy()
                    tech_params_char1 = tech_params_char1.add_suffix('_char1')
                    tech_params_char1 = tech_params_char1.rename(columns={'char_normalized_char1': 'char1_normalized'})
                    
                    tech_params_char2 = tech_params[['char_normalized'] + available_tech_features].copy()
                    tech_params_char2 = tech_params_char2.add_suffix('_char2')
                    tech_params_char2 = tech_params_char2.rename(columns={'char_normalized_char2': 'char2_normalized'})
                    
                    for col in available_tech_features:
                        if f"{col}_char1" in tech_params_char1.columns:
                            tech_params_char1[f"{col}_char1"] = pd.to_numeric(tech_params_char1[f"{col}_char1"], errors='coerce')
                        if f"{col}_char2" in tech_params_char2.columns:
                            tech_params_char2[f"{col}_char2"] = pd.to_numeric(tech_params_char2[f"{col}_char2"], errors='coerce')
                    
                    matchups_with_attrs = matchups_with_attrs.merge(
                        tech_params_char1, on='char1_normalized', how='left'
                    ).merge(
                        tech_params_char2, on='char2_normalized', how='left'
                    )
                    
                    self.use_tech_params = True
                    self.tech_features = available_tech_features
                else:
                    self.use_tech_params = False
            except Exception as e:
                print(f"Warning: Could not merge technical parameters: {e}")
                self.use_tech_params = False
        else:
            self.use_tech_params = False
        
        # Create features
        attributes = ['weight', 'recovery', 'speed', 'combo_game', 'projectiles', 
                      'killpower', 'ledgetrap', 'edgeguard', 'spacing', 'cheese']
        
        self.feature_names = []
        self.attributes = attributes
        
        # Attribute differences
        for attr in attributes:
            char1_col = f"{attr}_char1"
            char2_col = f"{attr}_char2"
            if char1_col in matchups_with_attrs.columns and char2_col in matchups_with_attrs.columns:
                matchups_with_attrs[f"{attr}_diff"] = (
                    matchups_with_attrs[char1_col] - matchups_with_attrs[char2_col]
                )
                self.feature_names.append(f"{attr}_diff")
        
        # Technical parameter differences (if available)
        if self.use_tech_params:
            for tech_feat in self.tech_features:
                char1_col = f"{tech_feat}_char1"
                char2_col = f"{tech_feat}_char2"
                if char1_col in matchups_with_attrs.columns and char2_col in matchups_with_attrs.columns:
                    matchups_with_attrs[f"{tech_feat}_diff"] = (
                        pd.to_numeric(matchups_with_attrs[char1_col], errors='coerce') - 
                        pd.to_numeric(matchups_with_attrs[char2_col], errors='coerce')
                    )
                    self.feature_names.append(f"{tech_feat}_diff")
        
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
        
        # Fill NaN with 0 (for missing technical params)
        self.X = self.X.fillna(0)
        
    def build_model(self):
        """Build and train the model"""
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
        print(f"Enhanced model trained! Accuracy: {accuracy*100:.2f}%")
        if self.use_tech_params:
            print(f"Using {len(self.feature_names)} features ({len(self.attributes)} attributes + {len(self.feature_names) - len(self.attributes)} technical params)")
        else:
            print(f"Using {len(self.feature_names)} features ({len(self.attributes)} attributes)")
    
    def predict(self, char1_name, char2_name):
        """Predict matchup outcome with symmetric predictions"""
        char1_norm = self.normalize_char_name(char1_name)
        char2_norm = self.normalize_char_name(char2_name)
        
        # Get character data
        char1_data = self.char_attrs[self.char_attrs['name'] == char1_norm]
        char2_data = self.char_attrs[self.char_attrs['name'] == char2_norm]
        
        if char1_data.empty:
            return None, f"Character '{char1_name}' not found"
        if char2_data.empty:
            return None, f"Character '{char2_name}' not found"
        
        # Build features
        features = []
        for attr in self.attributes:
            diff = char1_data[attr].values[0] - char2_data[attr].values[0]
            features.append(diff)
        
        # Add technical params if available (use 0 as default)
        if self.use_tech_params:
            # Try to get tech params for both characters
            # For now, use 0 as placeholder (would need tech_params loaded)
            for _ in self.tech_features:
                features.append(0)  # Placeholder - would need full tech params loading
        
        # Convert to DataFrame with feature names to avoid sklearn warning
        features_df = pd.DataFrame([features], columns=self.feature_names)
        
        # Predict both directions for symmetry
        pred1 = self.model.predict(features_df)[0]
        prob1 = self.model.predict_proba(features_df)[0]
        
        # Flipped direction
        features_flipped = [-f for f in features]
        features_flipped_df = pd.DataFrame([features_flipped], columns=self.feature_names)
        pred2 = self.model.predict(features_flipped_df)[0]
        prob2 = self.model.predict_proba(features_flipped_df)[0]
        
        # Use consensus
        if pred1 == 'Char1_Wins':
            winner1 = char1_norm
            prob_win1 = prob1[0] if self.model.classes_[0] == 'Char1_Wins' else prob1[1]
        else:
            winner1 = char2_norm
            prob_win1 = prob1[1] if self.model.classes_[0] == 'Char1_Wins' else prob1[0]
        
        if pred2 == 'Char1_Wins':
            winner2 = char2_norm  # char2 is char1 in flipped direction
            prob_win2 = prob2[0] if self.model.classes_[0] == 'Char1_Wins' else prob2[1]
        else:
            winner2 = char1_norm
            prob_win2 = prob2[1] if self.model.classes_[0] == 'Char1_Wins' else prob2[0]
        
        # Average probabilities
        if winner1 == winner2:
            final_winner = winner1
            final_prob = (prob_win1 + prob_win2) / 2
        else:
            prob_char1_avg = (prob_win1 + (1 - prob_win2)) / 2 if winner1 == char1_norm else ((1 - prob_win1) + prob_win2) / 2
            prob_char2_avg = 1 - prob_char1_avg
            
            if prob_char1_avg > prob_char2_avg:
                final_winner = char1_norm
                final_prob = prob_char1_avg
            else:
                final_winner = char2_norm
                final_prob = prob_char2_avg
        
        # Determine final prediction
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
    
    def get_feature_importance(self):
        """Get feature importance from the trained model"""
        if hasattr(self.model, 'feature_importances_'):
            return pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
        return None


"""
Interactive Matchup Predictor - GUI Version
Graphical user interface for matchup predictions
"""
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import warnings
warnings.filterwarnings('ignore')

# Import the predictor class
from matchup_predictor import MatchupPredictor

class MatchupPredictorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Super Smash Bros. Ultimate - Matchup Predictor")
        self.root.geometry("900x700")
        
        # Initialize predictor
        self.status_label = tk.Label(root, text="Loading model...", fg="blue")
        self.status_label.pack(pady=10)
        self.root.update()
        
        try:
            self.predictor = MatchupPredictor()
            self.characters = self.predictor.get_available_characters()
            self.status_label.config(text="Model loaded successfully!", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Error loading model: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            return
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Matchup Predictor", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        # Character selection frame
        select_frame = ttk.LabelFrame(main_frame, text="Select Characters", padding="10")
        select_frame.pack(fill=tk.X, pady=10)
        
        # Character 1
        char1_frame = ttk.Frame(select_frame)
        char1_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Label(char1_frame, text="Character 1:").pack()
        self.char1_combo = ttk.Combobox(char1_frame, values=self.characters, 
                                        state="readonly", width=25)
        self.char1_combo.pack(pady=5)
        self.char1_combo.bind("<<ComboboxSelected>>", self.on_character_change)
        
        # VS label
        vs_label = tk.Label(select_frame, text="VS", font=("Arial", 16, "bold"))
        vs_label.pack(side=tk.LEFT, padx=20)
        
        # Character 2
        char2_frame = ttk.Frame(select_frame)
        char2_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Label(char2_frame, text="Character 2:").pack()
        self.char2_combo = ttk.Combobox(char2_frame, values=self.characters,
                                        state="readonly", width=25)
        self.char2_combo.pack(pady=5)
        self.char2_combo.bind("<<ComboboxSelected>>", self.on_character_change)
        
        # Predict button
        self.predict_button = ttk.Button(select_frame, text="Predict Matchup", 
                                         command=self.predict_matchup)
        self.predict_button.pack(side=tk.LEFT, padx=20)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Prediction Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Results display
        self.results_text = tk.Text(results_frame, height=20, width=80, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, 
                                  command=self.results_text.yview)
        self.results_text.config(yscrollcommand=scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial message
        self.results_text.insert(tk.END, 
            "Welcome to the Matchup Predictor!\n\n"
            "1. Select two characters from the dropdown menus\n"
            "2. Click 'Predict Matchup' to see the prediction\n"
            "3. View detailed attribute comparisons below\n\n"
            "The model uses machine learning trained on tournament data\n"
            "to predict matchup outcomes based on character attributes.\n")
        self.results_text.config(state=tk.DISABLED)
        
    def on_character_change(self, event=None):
        """Enable predict button when both characters are selected"""
        if self.char1_combo.get() and self.char2_combo.get():
            if self.char1_combo.get() == self.char2_combo.get():
                self.predict_button.config(state=tk.DISABLED)
                self.status_label.config(text="Please select two different characters", fg="orange")
            else:
                self.predict_button.config(state=tk.NORMAL)
                self.status_label.config(text="Ready to predict", fg="green")
    
    def predict_matchup(self):
        """Predict matchup and display results"""
        char1 = self.char1_combo.get()
        char2 = self.char2_combo.get()
        
        if not char1 or not char2:
            messagebox.showwarning("Warning", "Please select both characters")
            return
        
        if char1 == char2:
            messagebox.showwarning("Warning", "Please select two different characters")
            return
        
        self.status_label.config(text="Predicting...", fg="blue")
        self.root.update()
        
        result, error = self.predictor.predict(char1, char2)
        
        if error:
            self.status_label.config(text="Error occurred", fg="red")
            messagebox.showerror("Error", error)
            return
        
        # Display results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Format results
        output = f"{'='*70}\n"
        output += f"MATCHUP PREDICTION: {result['char1']} vs {result['char2']}\n"
        output += f"{'='*70}\n\n"
        
        # Winner prediction
        if result['prediction'] == 'Char1_Wins':
            winner = result['char1']
            confidence = result['probabilities']['Char1_Wins']
        else:
            winner = result['char2']
            confidence = result['probabilities']['Char2_Wins']
        
        output += f"PREDICTED WINNER: {winner}\n"
        output += f"Confidence: {confidence*100:.1f}%\n\n"
        
        output += f"Win Probabilities:\n"
        output += f"  {result['char1']}: {result['probabilities'].get('Char1_Wins', 0)*100:.1f}%\n"
        output += f"  {result['char2']}: {result['probabilities'].get('Char2_Wins', 0)*100:.1f}%\n\n"
        
        # Attribute comparison
        output += f"{'='*70}\n"
        output += "ATTRIBUTE COMPARISON\n"
        output += f"{'='*70}\n"
        output += f"{'Attribute':<20} {result['char1']:<20} {result['char2']:<20} {'Advantage':<15}\n"
        output += "-" * 70 + "\n"
        
        for attr, values in result['comparison'].items():
            diff = values['difference']
            if abs(diff) < 0.1:
                advantage = "≈ Even"
            elif diff > 0:
                advantage = f"{result['char1']} +{diff:.1f}"
            else:
                advantage = f"{result['char2']} +{abs(diff):.1f}"
            
            output += f"{attr.title():<20} {values[result['char1']]:<20.1f} "
            output += f"{values[result['char2']]:<20.1f} {advantage:<15}\n"
        
        output += f"\n{'='*70}\n"
        output += "Note: Predictions are based on character attributes and tournament data.\n"
        output += "Actual matchups depend on player skill, stage selection, and meta trends.\n"
        
        self.results_text.insert(tk.END, output)
        self.results_text.config(state=tk.DISABLED)
        
        self.status_label.config(text=f"Prediction complete! {winner} predicted to win", fg="green")


def main():
    """Run the GUI application"""
    root = tk.Tk()
    app = MatchupPredictorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()


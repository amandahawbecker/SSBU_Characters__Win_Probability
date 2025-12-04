"""
Interactive Matchup Predictor - Streamlit Version
Web-based interface for matchup predictions with visualization support
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
from pathlib import Path
import sys

# Add parent directory to path to import matchup_predictor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import enhanced predictor first, fallback to backup
try:
    from matchup_predictor_enhanced import EnhancedMatchupPredictor as MatchupPredictor
    USE_ENHANCED = True
except ImportError:
    try:
        from matchup_predictor_backup import MatchupPredictor
        USE_ENHANCED = False
    except ImportError:
        # If that fails, try adding the current directory to path
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        try:
            from matchup_predictor_enhanced import EnhancedMatchupPredictor as MatchupPredictor
            USE_ENHANCED = True
        except ImportError:
            try:
                from matchup_predictor_backup import MatchupPredictor
                USE_ENHANCED = False
            except ImportError:
                st.error("Could not import MatchupPredictor. Please ensure matchup_predictor_enhanced.py or matchup_predictor_backup.py is in the same directory.")
                st.stop()

# Page configuration
st.set_page_config(
    page_title="SSBU Matchup Predictor",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .winner-text {
        font-size: 3rem;
        font-weight: bold;
        color: #ffffff;
        background-color: #28a745;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: winnerSlideIn 0.6s ease-out, winnerGlow 2s ease-in-out infinite;
    }
    .confidence-text {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        margin-top: 0.5rem;
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }
    .vs-symbol {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    @keyframes winnerSlideIn {
        0% {
            opacity: 0;
            transform: translateY(-30px) scale(0.9);
        }
        50% {
            transform: translateY(5px) scale(1.02);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    @keyframes winnerGlow {
        0%, 100% {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 0 20px rgba(40, 167, 69, 0.3);
        }
        50% {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 0 30px rgba(40, 167, 69, 0.6);
        }
    }
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .prediction-container {
        animation: containerSlideIn 0.5s ease-out;
    }
    @keyframes containerSlideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .win-probability-container {
        text-align: center;
        margin: 1rem 0;
    }
    .win-probability-spacer {
        padding: 0 30px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_predictor():
    """Load the matchup predictor model (cached)"""
    try:
        import os
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "1_Data_Files"
        
        # Enhanced predictor can take data_dir parameter
        if USE_ENHANCED:
            predictor = MatchupPredictor(data_dir=str(data_dir) if data_dir.exists() else None)
        else:
            # Backup predictor expects CSV files in current directory
            original_dir = os.getcwd()
            if data_dir.exists():
                os.chdir(str(data_dir))
                predictor = MatchupPredictor()
                os.chdir(original_dir)
            else:
                predictor = MatchupPredictor()
        
        return predictor, None
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        return None, error_msg

def find_visualization_files():
    """Find all visualization files from model scripts"""
    script_dir = Path(__file__).parent
    
    # Use local directories - ensure we're looking in the correct visualization directory
    viz_dir = script_dir / "3_Visualizations"
    results_dir = script_dir / "results"
    
    viz_files = {}
    csv_files = {}
    
    # Search for ALL PNG files in visualizations directory
    if viz_dir.exists():
        # Find all PNG files in the visualizations directory
        for png_file in viz_dir.glob("*.png"):
            # Use filename without extension as key
            key = png_file.stem
            if key not in viz_files:
                viz_files[key] = str(png_file)
        
        # Also check for JPG files
        for jpg_file in viz_dir.glob("*.jpg"):
            key = jpg_file.stem
            if key not in viz_files:
                viz_files[key] = str(jpg_file)
    
    # Feature importance CSV files from old scripts
    feature_importance_files = {
        'enhanced': 'feature_importance_enhanced.csv',
        'classifier': 'feature_importance_classifier.csv',
        'basic': 'feature_importance.csv',
    }
    
    # Search for feature importance CSV files
    if results_dir.exists():
        for key, filename in feature_importance_files.items():
            filepath = results_dir / filename
            if filepath.exists() and key not in csv_files:
                csv_files[key] = str(filepath)
    
    return viz_files, csv_files

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">Super Smash Bros. Ultimate Matchup Predictor</h1>', 
                unsafe_allow_html=True)
    
    # Load predictor
    predictor, error = load_predictor()
    
    if error:
        st.error(f"Error loading model: {error}")
        st.info("Please ensure all required data files are in the correct location.")
        return
    
    # Get available characters
    try:
        characters = predictor.get_available_characters()
    except Exception as e:
        st.error(f"Error getting character list: {e}")
        return
    
    # Create tabs
    tab1, tab2 = st.tabs(["Matchup Predictor", "Visualizations"])
    
    with tab1:
        st.header("Predict Matchup Outcomes")
        st.markdown("Select two characters to predict the matchup outcome based on ML models trained on tournament data.")
        
        # Character selection first
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            char1 = st.selectbox(
                "Character 1",
                options=[""] + characters,
                index=0,
                key="char1"
            )
        
        with col2:
            st.markdown("<div class='vs-symbol'>VS</div>", unsafe_allow_html=True)
        
        with col3:
            char2 = st.selectbox(
                "Character 2",
                options=[""] + characters,
                index=0,
                key="char2"
            )
        
        # Predict button below character selection
        predict_button = st.button("Predict Matchup", type="primary", width='stretch')
        
        # Prediction logic
        if predict_button:
            if not char1 or not char2:
                st.warning("Please select both characters")
            elif char1 == char2:
                st.warning("Please select two different characters")
            else:
                with st.spinner("Predicting matchup..."):
                    result, error = predictor.predict(char1, char2)
                    
                    if error:
                        st.error(f"Error: {error}")
                    else:
                        # Display results with animation
                        st.markdown("---")
                        
                        # Winner prediction
                        if result['prediction'] == 'Char1_Wins':
                            winner = result['char1']
                            confidence = result['probabilities']['Char1_Wins']
                        else:
                            winner = result['char2']
                            confidence = result['probabilities']['Char2_Wins']
                        
                        # Winner display with animation container
                        st.markdown(f"""
                            <div class="prediction-container">
                                <p class="winner-text">Predicted Winner: {winner}</p>
                                <p class="confidence-text">Confidence: {confidence*100:.1f}%</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Win probabilities - closer together
                        col1, col2 = st.columns([1, 1], gap="small")
                        with col1:
                            st.metric(
                                label=f"{result['char1']} Win Probability",
                                value=f"{result['probabilities'].get('Char1_Wins', 0)*100:.1f}%"
                            )
                        with col2:
                            st.metric(
                                label=f"{result['char2']} Win Probability",
                                value=f"{result['probabilities'].get('Char2_Wins', 0)*100:.1f}%"
                            )
                        
                        # Attribute comparison
                        st.markdown("---")
                        st.subheader("Attribute Comparison")
                        
                        comparison_data = []
                        for attr, values in result['comparison'].items():
                            diff = values['difference']
                            comparison_data.append({
                                'Attribute': attr.title(),
                                result['char1']: values[result['char1']],
                                result['char2']: values[result['char2']],
                                'Difference': diff,
                                'Advantage': result['char1'] if diff > 0.1 else (result['char2'] if diff < -0.1 else "≈ Even")
                            })
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        st.dataframe(
                            comparison_df,
                            width='stretch',
                            hide_index=True
                        )
                        
                        # Visualize attribute comparison
                        st.subheader("Attribute Comparison Chart")
                        chart_data = pd.DataFrame({
                            result['char1']: [v[result['char1']] for v in result['comparison'].values()],
                            result['char2']: [v[result['char2']] for v in result['comparison'].values()],
                        }, index=[attr.title() for attr in result['comparison'].keys()])
                        
                        st.bar_chart(chart_data)
                        
                        # Note
                        st.info("Note: Predictions are based on character attributes and tournament data. Actual matchups depend on player skill, stage selection, and meta trends.")
        
        # Initial instructions
        if not predict_button:
            st.info("Select two characters above and click 'Predict Matchup' to see predictions")
    
    with tab2:
        st.header("Feature Importance & Visualizations")
        st.markdown("Feature importance analysis from model training scripts")
        
        # Find visualization files
        viz_files, csv_files = find_visualization_files()
        
        # Display all visualization files from the visualizations directory
        if viz_files:
            for viz_name, viz_path in viz_files.items():
                with st.expander(f"{viz_name.replace('_', ' ').title()}", expanded=(viz_name == 'feature_importance')):
                    st.image(viz_path, width=850)
                    st.caption(f"File: `{viz_path}`")
        else:
            st.warning("No visualization files found in `2_Model_Scripts/3_Visualizations/` directory.")
            st.info("Please run the model training scripts to generate visualizations.")

if __name__ == "__main__":
    main()


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
    page_icon="🎮",
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
    .prediction-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .winner-text {
        font-size: 1.8rem;
        font-weight: bold;
        color: #28a745;
    }
    .confidence-text {
        font-size: 1.2rem;
        color: #6c757d;
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
    base_dir = Path(__file__).parent.parent
    
    # Check multiple possible locations
    viz_dirs = [
        base_dir / "visualizations",
        base_dir / "3_Visualizations",
        base_dir / "2_Model_Scripts" / "visualizations",
    ]
    
    result_dirs = [
        base_dir / "results",
        base_dir / "4_Results",
        base_dir / "2_Model_Scripts" / "results",
    ]
    
    viz_files = {}
    csv_files = {}
    
    # General visualization files
    general_viz = {
        'feature_importance': 'feature_importance.png',
    }
    
    # Feature importance CSV files from old scripts
    feature_importance_files = {
        'enhanced': 'feature_importance_enhanced.csv',
        'classifier': 'feature_importance_classifier.csv',
        'basic': 'feature_importance.csv',
    }
    
    # Search for visualization files
    for viz_dir in viz_dirs:
        if viz_dir.exists():
            for key, filename in general_viz.items():
                filepath = viz_dir / filename
                if filepath.exists() and key not in viz_files:
                    viz_files[key] = str(filepath)
    
    # Search for feature importance CSV files
    for result_dir in result_dirs:
        if result_dir.exists():
            for key, filename in feature_importance_files.items():
                filepath = result_dir / filename
                if filepath.exists() and key not in csv_files:
                    csv_files[key] = str(filepath)
    
    return viz_files, csv_files

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎮 Super Smash Bros. Ultimate Matchup Predictor</h1>', 
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
    tab1, tab2 = st.tabs(["🔮 Matchup Predictor", "📊 Visualizations"])
    
    with tab1:
        st.header("Predict Matchup Outcomes")
        st.markdown("Select two characters to predict the matchup outcome based on ML models trained on tournament data.")
        
        # Character selection
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            char1 = st.selectbox(
                "Character 1",
                options=[""] + characters,
                index=0,
                key="char1"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
        
        with col3:
            char2 = st.selectbox(
                "Character 2",
                options=[""] + characters,
                index=0,
                key="char2"
            )
        
        # Predict button
        predict_button = st.button("🚀 Predict Matchup", type="primary", use_container_width=True)
        
        # Prediction logic
        if predict_button:
            if not char1 or not char2:
                st.warning("⚠️ Please select both characters")
            elif char1 == char2:
                st.warning("⚠️ Please select two different characters")
            else:
                with st.spinner("Predicting matchup..."):
                    result, error = predictor.predict(char1, char2)
                    
                    if error:
                        st.error(f"❌ Error: {error}")
                    else:
                        # Display results
                        st.markdown("---")
                        
                        # Winner prediction
                        if result['prediction'] == 'Char1_Wins':
                            winner = result['char1']
                            confidence = result['probabilities']['Char1_Wins']
                        else:
                            winner = result['char2']
                            confidence = result['probabilities']['Char2_Wins']
                        
                        # Winner box
                        st.markdown(f"""
                            <div class="prediction-box">
                                <p class="winner-text">🏆 Predicted Winner: {winner}</p>
                                <p class="confidence-text">Confidence: {confidence*100:.1f}%</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Win probabilities
                        col1, col2 = st.columns(2)
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
                        st.subheader("📊 Attribute Comparison")
                        
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
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Visualize attribute comparison
                        st.subheader("📈 Attribute Comparison Chart")
                        chart_data = pd.DataFrame({
                            result['char1']: [v[result['char1']] for v in result['comparison'].values()],
                            result['char2']: [v[result['char2']] for v in result['comparison'].values()],
                        }, index=[attr.title() for attr in result['comparison'].keys()])
                        
                        st.bar_chart(chart_data)
                        
                        # Note
                        st.info("💡 Note: Predictions are based on character attributes and tournament data. Actual matchups depend on player skill, stage selection, and meta trends.")
        
        # Initial instructions
        if not predict_button:
            st.info("👆 Select two characters above and click 'Predict Matchup' to see predictions")
    
    with tab2:
        st.header("📊 Feature Importance & Visualizations")
        st.markdown("Feature importance analysis from model training scripts")
        
        # Find visualization files
        viz_files, csv_files = find_visualization_files()
        
        # Display feature importance visualization if available
        if 'feature_importance' in viz_files:
            st.subheader("📈 Feature Importance Visualization")
            st.image(viz_files['feature_importance'], use_container_width=True)
            st.caption("Feature importance chart from create_visualizations.py")
        
        # Show feature importance from model scripts
        st.subheader("📊 Feature Importance by Model")
        st.markdown("Feature importance rankings from different model training scripts")
        
        # Check for feature importance CSV files
        base_dir = Path(__file__).parent.parent
        results_dirs = [
            base_dir / "4_Results",
            base_dir / "results",
            base_dir / "2_Model_Scripts" / "results",
        ]
        
        # Enhanced Classifier Feature Importance
        enhanced_found = False
        for results_dir in results_dirs:
            enhanced_fi = results_dir / "feature_importance_enhanced.csv"
            if enhanced_fi.exists():
                enhanced_found = True
                with st.expander("📊 Enhanced Classifier Feature Importance (with technical parameters)", expanded=True):
                    try:
                        fi_df = pd.read_csv(enhanced_fi)
                        st.dataframe(fi_df.head(15), use_container_width=True, hide_index=True)
                        st.caption("From build_enhanced_classifier.py - includes technical parameters like movement speeds, gravity, etc.")
                        st.info("**Model**: Random Forest with enhanced features (attribute differences + technical parameters)")
                    except Exception as e:
                        st.error(f"Error loading: {e}")
                break
        
        # Binary Classifier Feature Importance
        classifier_found = False
        for results_dir in results_dirs:
            classifier_fi = results_dir / "feature_importance_classifier.csv"
            if classifier_fi.exists():
                classifier_found = True
                with st.expander("📊 Binary Classifier Feature Importance"):
                    try:
                        fi_df = pd.read_csv(classifier_fi)
                        st.dataframe(fi_df.head(15), use_container_width=True, hide_index=True)
                        st.caption("From build_matchup_classifier.py - three-class and binary classification models")
                        st.info("**Model**: Random Forest with basic attribute differences")
                    except Exception as e:
                        st.error(f"Error loading: {e}")
                break
        
        # Basic Model Feature Importance
        basic_found = False
        for results_dir in results_dirs:
            basic_fi = results_dir / "feature_importance.csv"
            if basic_fi.exists():
                basic_found = True
                with st.expander("📊 Basic Model Feature Importance"):
                    try:
                        fi_df = pd.read_csv(basic_fi)
                        st.dataframe(fi_df.head(15), use_container_width=True, hide_index=True)
                        st.caption("From build_matchup_model.py - regression model for winrate prediction")
                        st.info("**Model**: Random Forest regression on matchup winrates")
                    except Exception as e:
                        st.error(f"Error loading: {e}")
                break
        
        # Show feature importance from current predictor if available
        if predictor and hasattr(predictor, 'get_feature_importance'):
            with st.expander("📊 Current Predictor Feature Importance"):
                try:
                    fi_df = predictor.get_feature_importance()
                    if fi_df is not None:
                        st.dataframe(fi_df.head(15), use_container_width=True, hide_index=True)
                        st.caption("From the currently loaded matchup predictor model")
                except Exception as e:
                    st.warning(f"Could not get feature importance from predictor: {e}")
        
        # Warning if no files found
        if not enhanced_found and not classifier_found and not basic_found and 'feature_importance' not in viz_files:
            st.warning("⚠️ No feature importance files found. Please run the model training scripts first:")
            st.info("""
            **To generate feature importance files, run:**
            - `build_enhanced_classifier.py` → generates `feature_importance_enhanced.csv`
            - `build_matchup_classifier.py` → generates `feature_importance_classifier.csv`
            - `build_matchup_model.py` → generates `feature_importance.csv`
            - `create_visualizations.py` → generates `feature_importance.png`
            
            These scripts save their results to the `4_Results/` or `results/` directory.
            """)
        
        # File locations info
        with st.expander("ℹ️ File Locations"):
            if viz_files:
                st.write("**Visualization Files Found:**")
                for key, path in viz_files.items():
                    st.write(f"- {key}: `{path}`")
            
            if csv_files:
                st.write("**Feature Importance CSV Files Found:**")
                for key, path in csv_files.items():
                    st.write(f"- {key}: `{path}`")
            
            if not viz_files and not csv_files:
                st.write("No files found. Please run the model training scripts to generate feature importance files.")

if __name__ == "__main__":
    main()


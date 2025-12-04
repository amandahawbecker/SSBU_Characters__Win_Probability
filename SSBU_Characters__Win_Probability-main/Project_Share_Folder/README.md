# Project Share Folder - Super Smash Bros. Ultimate Matchup Prediction

This folder contains all important files organized for easy sharing with team members.

**Note:** All scripts use relative paths, so this folder can be located anywhere on your system (e.g., `C:\Project_Share_Folder` or any other location). The scripts will automatically find data files in the correct subdirectories.

## 📁 Folder Structure

### 1_Data_Files/
- Raw data files (CSV)
- Character attributes and tournament matchup data
- Cleaned training datasets

### 2_Model_Scripts/
- Python scripts to build and train models
- Data extraction and preprocessing scripts

### 3_Visualizations/
- PNG image files of charts and graphs
- Heatmaps, distributions, and analysis plots

### 4_Results/
- Model performance results (CSV)
- Feature importance rankings
- Confusion matrices and metrics

### 5_Documentation/
- Complete project documentation
- Methodologies, summaries, and guides
- Presentation materials

### 6_Interactive_Tools/
- GUI and command-line prediction tools
- Requirements.txt for dependencies

## 🚀 Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r 6_Interactive_Tools/requirements.txt
   ```

2. **Run GUI Predictor:**
   ```bash
   python 6_Interactive_Tools/matchup_predictor_gui.py
   ```

3. **Read Documentation:**
   - Start with: `5_Documentation/README.md`
   - Then: `5_Documentation/FINAL_PROJECT_SUMMARY.md`
   - For presentation: `5_Documentation/PRESENTATION_GUIDE.md`

## 📊 Key Results

- **Model Accuracy:** 84-85% (Binary Classification)
- **Dataset Size:** 1,857 matchup pairs
- **Features:** 18 (10 attributes + 8 technical parameters)
- **Best Model:** Random Forest Classifier

## 📝 Important Files

**Must Read First:**
- `5_Documentation/FINAL_PROJECT_SUMMARY.md` - Complete project overview
- `5_Documentation/EXECUTIVE_SUMMARY.md` - Quick summary

**For Presentation:**
- `5_Documentation/PRESENTATION_GUIDE.md` - Presentation guide
- `5_Documentation/PRESENTATION_SLIDES_OUTLINE.md` - Slide outline

**Key Visualizations:**
- `3_Visualizations/matchup_matrix_heatmap_with_steve.png` - Main matchup heatmap
- `3_Visualizations/character_usage_ranking.png` - Character popularity
- `3_Visualizations/confusion_matrix_plot_enhanced.png` - Model performance

## 🎯 Project Highlights

✅ Tournament data from 11M+ matches analyzed
✅ Machine learning models with 85%+ accuracy
✅ Comprehensive visualizations and analysis
✅ Interactive prediction tools (GUI and CLI)
✅ Complete documentation and methodology

Generated: 1764802493.8365068

# Super Smash Bros. Ultimate - Matchup Prediction Project

## 🎮 Overview

This project uses machine learning to predict character matchup outcomes in Super Smash Bros. Ultimate. The models are trained on tournament data and character attributes to predict which character would likely win in a matchup.

## 📊 Project Features

✅ **Tournament Data Analysis** - 11M+ tournament matches analyzed  
✅ **Machine Learning Models** - Classification models with 85%+ accuracy  
✅ **Technical Parameters** - Includes movement stats, speeds, and frame data  
✅ **Comprehensive Visualizations** - 7+ charts and graphs  
✅ **Interactive Tools** - GUI and command-line prediction interfaces  

## 🚀 Quick Start

### 1. Predict a Matchup (GUI - Recommended)
```bash
python matchup_predictor_gui.py
```
Opens a graphical interface where you can:
- Select characters from dropdown menus
- Get instant matchup predictions
- View detailed attribute comparisons

### 2. Predict a Matchup (Command-Line)
```bash
python matchup_predictor.py
```
Interactive text-based interface for matchup predictions.

### 3. View Visualizations
All visualization PNG files are in the project directory:
- `feature_importance.png` - Which attributes matter most
- `matchup_matrix_heatmap.png` - Matchup win rates heatmap
- `winrate_distribution.png` - Win rate distributions
- And more!

## 📁 Project Structure

### Core Files:
- `matchup_predictor.py` - Command-line prediction tool
- `matchup_predictor_gui.py` - GUI prediction tool
- `build_enhanced_classifier.py` - Model with technical parameters
- `create_visualizations.py` - Generate all visualizations

### Data Files:
- `character_matchups.csv` - Tournament matchup data
- `smash.csv` - Character attributes
- `ultimate_param.csv` - Technical parameters

### Documentation:
- `PROJECT_COMPLETE_SUMMARY.md` - Complete project summary
- `README.md` - This file

## 📈 Model Performance

- **Accuracy**: 83-85% in binary classification
- **Features**: 18 (10 attributes + 8 technical parameters)
- **Best Model**: Random Forest Classifier

### Most Important Features:
1. Weight difference
2. Killpower difference
3. Combo game difference
4. Edgeguard difference
5. Ledgetrap difference

## 🔧 Requirements

```bash
pip install pandas numpy scikit-learn matplotlib seaborn
```

## 📖 Usage Examples

### Example 1: Predict Mario vs Fox
1. Run `python matchup_predictor_gui.py`
2. Select "Mario" for Character 1
3. Select "Fox" for Character 2
4. Click "Predict Matchup"
5. View results!

### Example 2: Generate All Visualizations
```bash
python create_visualizations.py
```

### Example 3: Rebuild Enhanced Model
```bash
python build_enhanced_classifier.py
```

## 📊 Visualizations

Run `create_visualizations.py` to generate:
- Feature importance rankings
- Matchup matrix heatmap
- Win rate distributions
- Character attribute comparisons
- Model performance comparisons

## 🎯 Key Insights

1. **Classification works better** than regression (85% vs 6%)
2. **Weight and killpower** are most important for matchups
3. **Most matchups are one-sided** (72% favor one character)
4. **Technical parameters add value** - movement stats matter!

## 📝 Project Report

See `PROJECT_COMPLETE_SUMMARY.md` for:
- Complete methodology
- Results and analysis
- Future work suggestions
- Presentation guidelines

## 🤝 Contributing

This is an academic project. For questions or improvements:
1. Review the code documentation
2. Check `PROJECT_COMPLETE_SUMMARY.md`
3. Test with the interactive tools

## 📄 License

Academic project - DTSC201

---

**Enjoy predicting matchups! 🎮🏆**


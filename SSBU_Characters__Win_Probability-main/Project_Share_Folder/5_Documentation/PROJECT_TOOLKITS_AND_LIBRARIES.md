# Project Toolkits and Libraries

## 📦 Complete Toolkit List

This project uses a comprehensive set of Python libraries for data analysis, machine learning, visualization, and interactive tools.

---

## 🎯 Core Libraries

### **1. Data Processing & Analysis**

#### **pandas** ✅

- **Purpose**: Data manipulation and analysis
- **Used For**:
  - Loading CSV files
  - Data cleaning and preprocessing
  - Merging datasets
  - Data transformations
- **Examples**: Reading `smash.csv`, `character_matchups.csv`, database queries

#### **numpy** ✅

- **Purpose**: Numerical computing
- **Used For**:
  - Array operations
  - Mathematical computations
  - Feature vector creation
- **Examples**: Creating feature arrays for model input

#### **sqlite3** ✅

- **Purpose**: Database operations
- **Used For**:
  - Connecting to tournament database
  - Querying tournament data
  - Extracting matchup information
- **Examples**: `extract_matchup_data.py`, database exploration scripts

---

## 🤖 Machine Learning Libraries

### **2. Scikit-learn (sklearn)** ✅

**Primary ML Framework**

#### **sklearn.model_selection**

- `train_test_split` - Data splitting (80/20)
- `cross_val_score` - Cross-validation
- `StratifiedKFold` - Stratified cross-validation

#### **sklearn.ensemble**

- `RandomForestClassifier` - Main ML model
  - Used for matchup prediction
  - Handles class imbalance
  - Provides feature importance

#### **sklearn.metrics**

- `accuracy_score` - Model accuracy
- `classification_report` - Detailed metrics
- `confusion_matrix` - Prediction breakdown
- `precision_score`, `recall_score`, `f1_score` - Performance metrics
- `roc_auc_score` - ROC-AUC score

#### **sklearn.preprocessing**

- `label_binarize` - Label encoding (when needed)

---

## 📊 Visualization Libraries

### **3. matplotlib** ✅

- **Purpose**: Creating plots and charts
- **Used For**:
  - Feature importance plots
  - Win rate distributions
  - Confusion matrix visualizations
  - Character attribute comparisons
- **Backends**:
  - `matplotlib.backends.backend_tkagg` - GUI integration

### **4. seaborn** ✅

- **Purpose**: Statistical visualization
- **Used For**:
  - Heatmaps (matchup matrices)
  - Advanced styling
  - Correlation plots
- **Styles**: `whitegrid`, color palettes

---

## 📈 Statistical Analysis Libraries

### **5. scipy.stats** ✅

- **Purpose**: Statistical tests
- **Used For**:
  - `pearsonr` - Pearson correlation
  - `spearmanr` - Spearman correlation
- **Examples**: Correlation analysis in `correlation_analysis.py`

---

## 🖥️ GUI & Interactive Tools

### **6. tkinter** ✅

- **Purpose**: GUI creation
- **Used For**:
  - Interactive matchup predictor GUI
  - Character selection dropdowns
  - Results display
- **Modules**:
  - `tkinter.ttk` - Themed widgets
  - `tkinter.messagebox` - Error messages

---

## 📄 Data File Handling

### **7. openpyxl** ✅

- **Purpose**: Excel file reading
- **Used For**:
  - Reading `Ultimate Frame Data.xlsx`
  - Frame data extraction
- **Note**: Optional dependency

### **8. json** ✅

- **Purpose**: JSON parsing
- **Used For**:
  - Parsing character data from database
  - Player character information

### **9. pickle** ✅

- **Purpose**: Model serialization
- **Used For**:
  - Saving/loading trained models (if needed)

---

## 🔧 Utility Libraries

### **10. collections** ✅

- **Purpose**: Specialized container datatypes
- **Used For**:
  - `defaultdict` - Counting matchups
  - `Counter` - Character frequency analysis

### **11. itertools** ✅

- **Purpose**: Iterator tools
- **Used For**:
  - Generating matchup combinations
  - Coverage analysis

### **12. warnings** ✅

- **Purpose**: Warning management
- **Used For**:
  - Suppressing sklearn warnings
  - Clean output

---

## 📋 Complete Dependency List

### **Core Dependencies:**

```
pandas          # Data manipulation
numpy           # Numerical computing
scikit-learn    # Machine learning
matplotlib      # Plotting
seaborn         # Statistical visualization
scipy           # Scientific computing (stats module)
```

### **GUI Dependencies:**

```
tkinter         # GUI framework (built-in Python)
```

### **Database Dependencies:**

```
sqlite3         # Database operations (built-in Python)
```

### **Optional Dependencies:**

```
openpyxl        # Excel file reading
```

---

## 🚀 Installation

### **Standard Installation:**

```bash
pip install pandas numpy scikit-learn matplotlib seaborn scipy
```

### **For Excel Support:**

```bash
pip install openpyxl
```

### **Complete Installation:**

```bash
pip install pandas numpy scikit-learn matplotlib seaborn scipy openpyxl
```

---

## 📊 Usage by Category

### **Data Processing:**

- ✅ pandas - Primary data manipulation
- ✅ numpy - Numerical operations
- ✅ sqlite3 - Database queries
- ✅ json - Data parsing

### **Machine Learning:**

- ✅ scikit-learn - Complete ML framework
  - Model training (Random Forest)
  - Model evaluation (metrics)
  - Data splitting (train/test)

### **Visualization:**

- ✅ matplotlib - Plotting
- ✅ seaborn - Statistical plots

### **Statistical Analysis:**

- ✅ scipy.stats - Correlation tests

### **Interactive Tools:**

- ✅ tkinter - GUI creation

---

## 🎯 Key Libraries Breakdown

### **Most Used Libraries:**

1. **pandas** - Used in almost every script
2. **numpy** - Numerical operations throughout
3. **scikit-learn** - Core ML functionality
4. **matplotlib/seaborn** - All visualizations

### **Specialized Libraries:**

- **sqlite3** - Database operations only
- **tkinter** - GUI tool only
- **openpyxl** - Frame data reading only
- **scipy.stats** - Correlation analysis only

---

## 📝 Library Versions

**Note**: Project works with standard versions of these libraries. No specific version requirements.

### **Recommended Versions:**

```
pandas >= 1.0.0
numpy >= 1.19.0
scikit-learn >= 0.24.0
matplotlib >= 3.3.0
seaborn >= 0.11.0
scipy >= 1.5.0
```

---

## 🔍 What Each Library Does in This Project

### **pandas** - Data Foundation

- Loads all CSV files
- Merges character attributes with matchup data
- Cleans and preprocesses data
- Creates feature datasets

### **numpy** - Numerical Operations

- Creates feature arrays
- Mathematical computations
- Array manipulations for model input

### **scikit-learn** - Machine Learning

- Trains Random Forest Classifier
- Splits data into train/test sets
- Evaluates model performance
- Provides feature importance

### **matplotlib/seaborn** - Visualization

- Creates feature importance charts
- Generates matchup heatmaps
- Shows win rate distributions
- Displays confusion matrices

### **sqlite3** - Database Access

- Connects to tournament database
- Queries tournament sets
- Extracts matchup information

### **tkinter** - User Interface

- Creates interactive GUI
- Allows character selection
- Displays predictions

---

## ✅ Summary

**Total Libraries: 12+**

**Core Stack:**

- Data: pandas, numpy
- ML: scikit-learn
- Visualization: matplotlib, seaborn
- Stats: scipy.stats
- Database: sqlite3
- GUI: tkinter

**All libraries are well-established, widely-used, and standard in data science projects!** ✅

---

## 📚 Documentation Links

- [pandas Documentation](https://pandas.pydata.org/)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [matplotlib Documentation](https://matplotlib.org/)
- [seaborn Documentation](https://seaborn.pydata.org/)
- [numpy Documentation](https://numpy.org/)

---

**This toolkit stack is perfect for data science projects!** 🎯

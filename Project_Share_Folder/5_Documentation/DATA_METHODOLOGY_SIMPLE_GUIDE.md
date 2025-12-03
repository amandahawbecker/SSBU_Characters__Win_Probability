# Data and Methodology - Simple Guide

## 📊 DATA: What We Used

---

### **1. Tournament Database**
- **Source:** `ultimate_player_database.db`
- **Contains:** 11+ million tournament match results
- **What We Extracted:**
  - Which character won each match
  - Character matchup pairs (Mario vs Fox, etc.)
  - Win rates for each matchup

### **2. Character Attributes**
- **Source:** `smash.csv`
- **Contains:** Stats for 82 characters
- **Attributes:** Weight, Speed, Killpower, Recovery, etc. (10 total)

### **3. Technical Parameters**
- **Source:** `ultimate_param.csv`
- **Contains:** Movement speeds, physics stats (8 technical features)

---

## 🔄 METHODOLOGY: How It Works

---

### **STEP 1: Extract Matchup Data**

**From Tournament Database:**
```
Tournament Match → Player X (plays Mario) beats Player Y (plays Fox)
                  ↓
         Mario vs Fox matchup → Mario gets +1 win
```

**Result:** 2,432 matchup pairs with win rates

---

### **STEP 2: Merge Character Attributes**

**Combine:**
- Matchup win rates (from tournaments)
- Character attributes (from smash.csv)

**Result:** 1,857 matchups with complete data

---

### **STEP 3: Feature Engineering**

**Key Idea:** Use ATTRIBUTE DIFFERENCES, not absolute values

**Example: Mario vs Fox**
```
Weight:   Mario (98) - Fox (77) = +21  (Mario is heavier)
Speed:    Mario (5)  - Fox (8)  = -3   (Fox is faster)
Killpower: Mario (138) - Fox (121) = +17 (Mario has more)
```

**Why Differences?**
- Shows **comparative advantages**
- Works for any character pair
- Model learns: "Who has the advantage?"

**Features Created:** 18 total
- 10 attribute differences
- 8 technical parameter differences

---

### **STEP 4: Train Machine Learning Model**

**Algorithm:** Random Forest Classifier

**Process:**
1. Split data: 80% train (1,485), 20% test (372)
2. Train 100 decision trees
3. Each tree learns patterns from attribute differences
4. Trees vote together for final prediction

**Result:** Model learns which attributes predict wins

---

### **STEP 5: Make Predictions**

**For New Matchup (e.g., "Mario vs Fox"):**

1. **Get Attributes**
   - Mario: weight=98, speed=5, killpower=138...
   - Fox: weight=77, speed=8, killpower=121...

2. **Calculate Differences**
   - weight_diff = +21, speed_diff = -3, killpower_diff = +17...

3. **Feed to Model**
   - Model analyzes: "Mario has weight/killpower advantage"
   - Model predicts: "Mario wins" (86% confidence)

4. **Return Result**
   - Winner: Mario
   - Confidence: 86.1%

---

## 📈 MODEL PERFORMANCE

**Accuracy:** 83.33% on test data

**What This Means:**
- Model correctly predicts winner 83% of the time
- Better than random guessing (50%)
- Learned patterns from tournament data

---

## 🎯 KEY CONCEPTS

### **1. Attribute Differences**
- Model uses: `Char1_stat - Char2_stat`
- Not: Individual character stats
- Captures matchup dynamics

### **2. Random Forest**
- 100 decision trees
- Each tree learns different patterns
- Votes together for final answer

### **3. Pattern Learning**
- Model learned from 1,857 tournament matchups
- Identifies which attribute combinations predict wins
- Example: "High weight + high killpower = advantage"

---

## 📝 SIMPLE SUMMARY

**DATA:**
- Tournament results → Matchup win rates
- Character attributes → Stats for each character
- Combined → 1,857 matchups with complete data

**METHOD:**
1. Calculate attribute differences
2. Train Random Forest on tournament data
3. Model learns patterns
4. Predict new matchups

**RESULT:**
- 83% accurate predictions
- Understands which attributes matter most

---

**That's how the model works - simple but effective!** ✅


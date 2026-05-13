# FairCode: Mitigating Algorithmic Bias in AI
**Founder:** Yash Kewlani

## 📌 Project Overview
An AI awareness initiative and technical proof-of-concept demonstrating how to detect and reduce racial bias in predictive algorithms. This project uses the **COMPAS Criminal Justice dataset** to bridge the gap between pure coding and ethical AI development.

## 🛠 Technical Implementation
* **Language:** Python
* **Library:** Scikit-learn (Random Forest Classifier)
* **Dataset:** `compas-scores-raw.csv`
* **Core Skills:** Computational thinking, research analysis, and AI fundamentals.

## 📊 Results

### 1. The Problem: Biased Prediction (`unfair.py`)
The original model, trained with sensitive attributes (race), showed a significant **Fairness Gap**.
* **Finding:** Certain demographics were flagged as "High Risk" at a much higher rate regardless of underlying data.
* **Evidence:** `unfair.jpg`

### 2. The Solution: Mitigation (`fair.py`)
I engineered a fairer model by implementing **Attribute Dropping** and **Proxy Mitigation**.
* **The Fix:** Removed the primary "Race" variable and "Custody Status" (a high-correlation proxy for bias).
* **Finding:** The Fairness Gap was reduced significantly while maintaining predictive integrity.
* **Evidence:** `fair.jpg`

## 📂 Repository Contents
* `unfair.py` - Script demonstrating the initial algorithmic bias.
* `fair.py` - Mitigated script optimized for fairness.
* `compas-scores-raw.csv` - Dataset used for training and testing.
* `unfair.jpg` - Terminal output of the biased model.
* `fair.jpg` - Terminal output of the mitigated model.


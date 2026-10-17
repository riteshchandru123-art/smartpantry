# 🥦💰 SmartPantry Pro: NutriWallet

**Zero-Waste Precision Macros & Grocery Savings Engine** powered by **Gemini 2.5 Multimodal Vision**, **Plotly**, and **DevOps automation**.

> **"Hit your daily protein & calorie targets without burning your wallet or throwing out expired food."**

---

## 🌟 Key Upgraded Features

1. **🧾 Dual-Vision Intake (Fridge & Supermarket Receipts):**
   - **Fridge & Shelves:** Detects food items, estimates shelf-life, and calculates total calories, protein (g), carbs (g), and healthy fats (g).
   - **Receipt OCR:** Snap your paper grocery receipt (Walmart, Trader Joe's, Tesco, D-Mart, etc.). Gemini OCR extracts individual line items **and their purchase prices** to track the financial value of your fridge.
2. **🏋️‍♂️ Target-Locked Macro Meal Synthesis:**
   - Configure fitness objectives: *High-Protein Cut, Lean Muscle Bulk, Keto, or Budget Feast*.
   - Dial in exact target protein (e.g., 45g) and calorie constraints.
   - Generates recipes specifically formulated to hit your macro targets while prioritizing soon-to-expire groceries.
3. **💸 "Cost-Per-Plate" & Takeout Savings Calculator:**
   - Calculates the cost to cook at home vs. equivalent restaurant/DoorDash delivery orders.
   - Calculates **Protein Efficiency** (e.g., *\$0.05 per gram of protein*).
   - Computes live money saved per meal.
4. **📊 Daily Health & Wallet Tracker (Plotly):**
   - Interactive macro donut charts and daily progress rings.
   - One-click "I Cooked This Meal!" logger tracking daily cumulative protein and dollars saved.

---

## 🛠️ Quickstart (Run Locally)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your API Key
Add your free Gemini API key from [Google AI Studio](https://aistudio.google.com) to `.env`:
```env
GEMINI_API_KEY=your_actual_key_here
```

### 3. Launch App
```bash
python -m streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 🧪 Running Automated Tests
```bash
python -m unittest discover tests/
```

---

## 🐳 Docker Execution
```bash
docker compose up --build
```

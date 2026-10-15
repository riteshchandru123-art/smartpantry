# 🥦 SmartPantry AI

**Zero-Waste Smart Fridge Assistant** powered by **Gemini 1.5/2.5 Multimodal Vision**, **Streamlit**, and **DevOps automation**.

---

## 🌟 Key Features

1. **📸 Multimodal Vision Scanning:** Snap a picture of your fridge, pantry, or grocery receipt. Gemini detects ingredients, estimates quantities, and predicts realistic expiration windows.
2. **🧺 Expiry Watchdog:** Visual dashboard with expiration warnings (urgent alerts for items expiring within 3 days).
3. **👨‍🍳 Zero-Waste AI Chef:** Autonomous recipe generator prioritizing ingredients closest to spoiling, adapting to meal type (Breakfast, Lunch, Dinner) and dietary restrictions (Vegetarian, High-Protein, Keto, etc.).
4. **🚀 Cloud & DevOps Ready:**
   - Production-ready `Dockerfile` (supports Cloud Run `$PORT`).
   - `docker-compose.yml` for 1-command containerized execution.
   - GitHub Actions CI/CD pipeline with automated `pytest` and container build.

---

## 🛠️ Quickstart (Run Locally)

### 1. Clone & Install Dependencies
```bash
cd smartpantry
pip install -r requirements.txt
```

### 2. Configure Your API Key
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your free Gemini API key from [Google AI Studio](https://aistudio.google.com):
```env
GEMINI_API_KEY=your_actual_key_here
```
*(You can also enter your key directly inside the app's sidebar).*

### 3. Run the App
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests
```bash
pytest -v tests/
```

---

## 🐳 Running with Docker

### Using Docker Compose
```bash
docker compose up --build
```
Access the app at `http://localhost:8501`.

---

## ☁️ Deploying to the Cloud (Google Cloud Run in 2 Minutes)

1. Make sure you have Google Cloud SDK installed.
2. Build and deploy directly with:
```bash
gcloud run deploy smartpantry \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key_here
```
You will get a live HTTPS URL you can open on your phone or share with anyone!

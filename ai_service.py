import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from PIL import Image

# --- Pydantic Data Schemas ---

class DetectedItem(BaseModel):
    name: str = Field(description="Name of the food item or ingredient")
    quantity: str = Field(description="Estimated quantity, e.g., '1 bunch', '250ml', '4 eggs'")
    category: str = Field(description="One of: Produce, Dairy, Meat/Protein, Bakery, Condiments, Beverages, Pantry, Other")
    estimated_shelf_life_days: int = Field(description="Realistic shelf-life in days from today")
    estimated_price: float = Field(default=2.50, description="Estimated purchase price in USD")
    calories: int = Field(default=100, description="Estimated total calories for this quantity")
    protein_g: float = Field(default=5.0, description="Estimated grams of protein")
    carbs_g: float = Field(default=10.0, description="Estimated grams of carbohydrates")
    fat_g: float = Field(default=2.0, description="Estimated grams of healthy fat")

class VisionAnalysisResult(BaseModel):
    items: List[DetectedItem] = Field(description="List of detected food items and ingredients")

class ReceiptItem(BaseModel):
    name: str = Field(description="Name of the purchased grocery item")
    quantity: str = Field(description="Quantity or weight purchased")
    price: float = Field(description="Actual price paid as printed on receipt")
    category: str = Field(description="One of: Produce, Dairy, Meat/Protein, Bakery, Condiments, Beverages, Pantry, Other")
    estimated_shelf_life_days: int = Field(default=7, description="Estimated fresh shelf-life days")
    calories: int = Field(default=150, description="Estimated total calories")
    protein_g: float = Field(default=8.0, description="Estimated protein grams")
    carbs_g: float = Field(default=15.0, description="Estimated carb grams")
    fat_g: float = Field(default=3.0, description="Estimated fat grams")

class ReceiptAnalysisResult(BaseModel):
    store_name: str = Field(description="Supermarket or store name")
    total_spent: float = Field(description="Total receipt amount")
    items: List[ReceiptItem] = Field(description="All grocery items extracted from receipt")

class MacroNutritionalProfile(BaseModel):
    calories: int = Field(description="Total calories per serving")
    protein_g: float = Field(description="Total grams of protein per serving")
    carbs_g: float = Field(description="Total grams of carbohydrates per serving")
    fat_g: float = Field(description="Total grams of fat per serving")

class CostAnalysis(BaseModel):
    cost_to_cook_per_serving: float = Field(description="Estimated cost in USD to cook this meal at home")
    takeout_equivalent_cost: float = Field(description="Estimated cost if ordered from a restaurant/takeout (e.g. $14-18)")
    money_saved_per_serving: float = Field(description="Dollars saved per serving by cooking from pantry")
    cost_per_gram_protein: float = Field(description="Cost efficiency: cost to cook divided by protein grams")

class Recipe(BaseModel):
    title: str = Field(description="Creative, appetizing recipe title")
    prep_time_minutes: int = Field(description="Estimated prep time in minutes")
    cook_time_minutes: int = Field(description="Estimated cook time in minutes")
    servings: int = Field(description="Number of servings")
    ingredients_used: List[str] = Field(description="Ingredients used from the user's pantry")
    additional_needed: List[str] = Field(description="Common pantry staples or optional extra items needed")
    instructions: List[str] = Field(description="Numbered step-by-step cooking instructions")
    zero_waste_tip: str = Field(description="Tip on how this recipe prevents food waste or utilizes scraps")
    nutritional_profile: MacroNutritionalProfile = Field(description="Per-serving nutritional macro breakdown")
    cost_analysis: CostAnalysis = Field(description="Cost and financial savings analysis")
    macro_alignment_tip: str = Field(description="How this meal supports the user's fitness/macro target")


# --- Vision Extraction Functions ---

def analyze_pantry_image(image: Image.Image, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Analyzes fridge/pantry photo with Gemini Multimodal Vision,
    extracting ingredients, shelf life, macro estimates, and estimated values.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Missing GEMINI_API_KEY. Please set it in the sidebar.")

    prompt = (
        "You are NutriWallet's multimodal computer vision system. Inspect this photo of a refrigerator, "
        "pantry shelf, or counter. Identify all distinct food items, produce, proteins, dairy, and ingredients visible. "
        "For each item:\n"
        "1. Estimate realistic quantity/volume.\n"
        "2. Predict shelf-life in days.\n"
        "3. Estimate realistic grocery price in USD.\n"
        "4. Estimate nutritional macros (Calories, Protein in grams, Carbs in grams, Fat in grams) for the detected amount."
    )

    try:
        from google import genai
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, image],
            config={
                'response_mime_type': 'application/json',
                'response_schema': VisionAnalysisResult,
            },
        )
        data = json.loads(response.text)
        today = datetime.now()
        results = []
        for item in data.get("items", []):
            days = item.get("estimated_shelf_life_days", 5)
            expiry_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
            results.append({
                "name": item["name"],
                "quantity": item["quantity"],
                "category": item["category"],
                "expiry_date": expiry_date,
                "price": round(float(item.get("estimated_price", 2.50)), 2),
                "calories": int(item.get("calories", 100)),
                "protein_g": round(float(item.get("protein_g", 5.0)), 1),
                "carbs_g": round(float(item.get("carbs_g", 10.0)), 1),
                "fat_g": round(float(item.get("fat_g", 2.0)), 1),
                "notes": f"Auto-detected. ~{days}d shelf life."
            })
        return results

    except Exception:
        # Fallback to legacy SDK
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=key)
        model = legacy_genai.GenerativeModel('gemini-1.5-flash')
        resp = model.generate_content([
            prompt + "\nReturn JSON with schema: {\"items\": [{\"name\": \"...\", \"quantity\": \"...\", \"category\": \"Produce\", \"estimated_shelf_life_days\": 5, \"estimated_price\": 3.0, \"calories\": 120, \"protein_g\": 4.0, \"carbs_g\": 15.0, \"fat_g\": 1.0}]}",
            image
        ])
        cleaned = resp.text.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(cleaned)
        today = datetime.now()
        results = []
        for item in data.get("items", []):
            days = item.get("estimated_shelf_life_days", 5)
            expiry_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
            results.append({
                "name": item["name"],
                "quantity": item["quantity"],
                "category": item.get("category", "Other"),
                "expiry_date": expiry_date,
                "price": round(float(item.get("estimated_price", 2.50)), 2),
                "calories": int(item.get("calories", 100)),
                "protein_g": round(float(item.get("protein_g", 5.0)), 1),
                "carbs_g": round(float(item.get("carbs_g", 10.0)), 1),
                "fat_g": round(float(item.get("fat_g", 2.0)), 1),
                "notes": f"Auto-detected. ~{days}d shelf life."
            })
        return results

def analyze_receipt_image(image: Image.Image, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Performs OCR and semantic parsing on a supermarket paper receipt,
    extracting purchased items, unit prices, store name, and estimating macros.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Missing GEMINI_API_KEY. Please set it in the sidebar.")

    prompt = (
        "You are NutriWallet's receipt OCR specialist. Inspect this paper supermarket receipt. "
        "Extract the store name, the total amount spent, and parse every individual food or grocery item "
        "along with its exact price as listed on the receipt. "
        "For each item, classify its category, estimate its shelf-life in days, and estimate its total nutritional profile."
    )

    try:
        from google import genai
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, image],
            config={
                'response_mime_type': 'application/json',
                'response_schema': ReceiptAnalysisResult,
            },
        )
        data = json.loads(response.text)
        today = datetime.now()
        items = []
        for item in data.get("items", []):
            days = item.get("estimated_shelf_life_days", 7)
            expiry_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
            items.append({
                "name": item["name"],
                "quantity": item.get("quantity", "1 pack"),
                "category": item.get("category", "Pantry"),
                "price": round(float(item.get("price", 0.0)), 2),
                "expiry_date": expiry_date,
                "calories": int(item.get("calories", 150)),
                "protein_g": round(float(item.get("protein_g", 8.0)), 1),
                "carbs_g": round(float(item.get("carbs_g", 15.0)), 1),
                "fat_g": round(float(item.get("fat_g", 3.0)), 1),
                "notes": f"Receipt from {data.get('store_name', 'Store')}."
            })
        return {
            "store_name": data.get("store_name", "Supermarket"),
            "total_spent": round(float(data.get("total_spent", 0.0)), 2),
            "items": items
        }
    except Exception as e:
        # Fallback to legacy SDK
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=key)
        model = legacy_genai.GenerativeModel('gemini-1.5-flash')
        resp = model.generate_content([
            prompt + "\nReturn JSON schema: {\"store_name\": \"...\", \"total_spent\": 25.50, \"items\": [{\"name\": \"...\", \"quantity\": \"...\", \"price\": 4.99, \"category\": \"Produce\", \"estimated_shelf_life_days\": 5, \"calories\": 100, \"protein_g\": 2.0, \"carbs_g\": 10.0, \"fat_g\": 1.0}]}",
            image
        ])
        cleaned = resp.text.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(cleaned)
        today = datetime.now()
        items = []
        for item in data.get("items", []):
            days = item.get("estimated_shelf_life_days", 7)
            items.append({
                "name": item["name"],
                "quantity": item.get("quantity", "1 pack"),
                "category": item.get("category", "Pantry"),
                "price": round(float(item.get("price", 0.0)), 2),
                "expiry_date": (today + timedelta(days=days)).strftime("%Y-%m-%d"),
                "calories": int(item.get("calories", 150)),
                "protein_g": round(float(item.get("protein_g", 8.0)), 1),
                "carbs_g": round(float(item.get("carbs_g", 15.0)), 1),
                "fat_g": round(float(item.get("fat_g", 3.0)), 1),
                "notes": f"Receipt from {data.get('store_name', 'Store')}."
            })
        return {
            "store_name": data.get("store_name", "Supermarket"),
            "total_spent": round(float(data.get("total_spent", 0.0)), 2),
            "items": items
        }


# --- Precision Macro & Cost-Per-Plate Recipe Generator ---

def generate_recipe(
    available_items: List[Dict[str, Any]],
    expiring_soon_items: List[Dict[str, Any]],
    fitness_goal: str = "High-Protein Cut",
    target_protein_g: int = 40,
    target_calories: int = 500,
    meal_type: str = "Dinner",
    max_time_minutes: int = 30,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a zero-waste recipe optimized for BOTH precision macros and cost savings.
    Calculates cost-to-cook, restaurant takeout equivalent cost, and dollars saved.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Missing GEMINI_API_KEY. Please set it in the sidebar.")

    pantry_summary = "\n".join([
        f"- {it['name']} (Qty: {it['quantity']}, Est. Price: ${it.get('price', 2.0):.2f}, ~{it.get('protein_g', 0)}g protein)"
        for it in available_items
    ])
    expiring_summary = "\n".join([
        f"- {it['name']} (Expiring: {it['expiry_date']})"
        for it in expiring_soon_items
    ])

    prompt = f"""
    You are NutriWallet's elite Sports Nutritionist and Zero-Waste Chef. 
    Create an appetizing, high-efficiency meal tailored to the user's fitness goal and budget.

    FITNESS & MACRO TARGETS:
    - Fitness Goal: {fitness_goal}
    - Target Protein per serving: ~{target_protein_g} grams
    - Target Calories per serving: ~{target_calories} kcal
    - Meal Type: {meal_type}
    - Max Cooking Time: {max_time_minutes} minutes

    CRITICAL INVENTORY PRIORITY:
    Use these items that are EXPIRING SOON:
    {expiring_summary if expiring_summary else "No urgent items expiring, pick from available inventory."}

    ALL AVAILABLE PANTRY INVENTORY:
    {pantry_summary}

    COST & FINANCIAL ANALYSIS RULES:
    1. Calculate realistic cost_to_cook_per_serving based on the ingredients used from the pantry (usually $2.00 - $4.50).
    2. Estimate takeout_equivalent_cost (what a restaurant or delivery app like UberEats/DoorDash would charge for this meal, typically $14.00 - $19.00).
    3. Calculate money_saved_per_serving = takeout_equivalent_cost - cost_to_cook_per_serving.
    4. Calculate cost_per_gram_protein = cost_to_cook_per_serving / protein_g.

    Return output in strict JSON format conforming to the Recipe schema.
    """

    try:
        from google import genai
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': Recipe,
            },
        )
        return json.loads(response.text)
    except Exception:
        # Fallback to legacy SDK
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=key)
        model = legacy_genai.GenerativeModel('gemini-1.5-flash')
        resp = model.generate_content(prompt + "\nReturn strictly JSON.")
        cleaned = resp.text.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(cleaned)

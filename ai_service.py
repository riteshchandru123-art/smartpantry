import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from PIL import Image

class DetectedItem(BaseModel):
    name: str = Field(description="Name of the food item or ingredient")
    quantity: str = Field(description="Estimated quantity, e.g., '1 bunch', '250ml', '3 pieces'")
    category: str = Field(description="One of: Produce, Dairy, Meat/Protein, Bakery, Condiments, Beverages, Pantry, Other")
    estimated_shelf_life_days: int = Field(description="Realistic shelf-life in days from today if stored properly")

class VisionAnalysisResult(BaseModel):
    items: List[DetectedItem] = Field(description="List of detected food items and ingredients")

class Recipe(BaseModel):
    title: str = Field(description="Creative, appetizing recipe title")
    prep_time_minutes: int = Field(description="Estimated prep time in minutes")
    cook_time_minutes: int = Field(description="Estimated cook time in minutes")
    servings: int = Field(description="Number of servings")
    ingredients_used: List[str] = Field(description="Ingredients used from the user's pantry")
    additional_needed: List[str] = Field(description="Common pantry staples or optional extra items needed")
    instructions: List[str] = Field(description="Numbered step-by-step cooking instructions")
    zero_waste_tip: str = Field(description="Tip on how this recipe prevents food waste or utilizes scraps")

def get_client(api_key: Optional[str] = None):
    """Initializes Google GenAI client."""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY is not set. Please provide it in the sidebar or in your .env file.")
    
    # Try importing from modern google-genai
    try:
        from google import genai
        return genai.Client(api_key=key)
    except ImportError:
        pass
    
    # Fallback to legacy google.generativeai if installed
    try:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=key)
        return legacy_genai
    except ImportError:
        raise ImportError("Please install google-genai (`pip install google-genai`).")

def analyze_pantry_image(image: Image.Image, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Analyzes an uploaded fridge, pantry, or grocery photo using Gemini Multimodal
    and returns a structured list of detected items with expiry estimates.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Missing GEMINI_API_KEY. Please set it in the sidebar.")

    try:
        from google import genai
        client = genai.Client(api_key=key)
        
        prompt = (
            "You are SmartPantry's computer vision system. Inspect this photo of a refrigerator, pantry, "
            "or grocery receipt. Identify all distinct food items, produce, drinks, or packaged ingredients visible. "
            "For each item, estimate the quantity, determine the appropriate category, and estimate realistic shelf life "
            "in days assuming typical refrigeration or pantry storage."
        )

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
                "notes": f"Auto-detected. Estimated ~{days} days fresh."
            })
        return results

    except Exception as e:
        # Check if legacy SDK fallback is needed
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=key)
            model = legacy_genai.GenerativeModel('gemini-1.5-flash')
            prompt = (
                "You are SmartPantry's vision system. Identify all food items/ingredients in this image. "
                "Return pure JSON with schema: {\"items\": [{\"name\": \"...\", \"quantity\": \"...\", \"category\": \"...\", \"estimated_shelf_life_days\": 4}]}"
            )
            resp = model.generate_content([prompt, image])
            cleaned_text = resp.text.strip().removeprefix("```json").removesuffix("```").strip()
            data = json.loads(cleaned_text)
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
                    "notes": f"Auto-detected. Estimated ~{days} days fresh."
                })
            return results
        except Exception:
            raise RuntimeError(f"Error processing image with Gemini AI: {str(e)}")

def generate_recipe(
    available_items: List[Dict[str, Any]],
    expiring_soon_items: List[Dict[str, Any]],
    dietary_preferences: str = "None",
    meal_type: str = "Dinner",
    max_time_minutes: int = 30,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a zero-waste recipe prioritizing expiring ingredients.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Missing GEMINI_API_KEY. Please set it in the sidebar.")

    pantry_summary = "\n".join([f"- {it['name']} ({it['quantity']})" for it in available_items])
    expiring_summary = "\n".join([f"- {it['name']} (Expiring: {it['expiry_date']})" for it in expiring_soon_items])

    prompt = f"""
    You are an expert Zero-Waste Chef. Create an appetizing, realistic recipe using the user's available pantry ingredients.
    
    CRITICAL PRIORITY: Heavily prioritize using these items that are EXPIRING SOON:
    {expiring_summary if expiring_summary else "No urgent items expiring, pick from available inventory."}
    
    ALL AVAILABLE PANTRY ITEMS:
    {pantry_summary}
    
    PREFERENCES:
    - Meal Type: {meal_type}
    - Dietary Restrictions: {dietary_preferences}
    - Max Time: {max_time_minutes} minutes
    
    You may assume the user has basic kitchen staples (salt, pepper, cooking oil, water).
    Provide output in strict structured JSON matching the Recipe schema.
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
    except Exception as e:
        # Fallback to legacy
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=key)
            model = legacy_genai.GenerativeModel('gemini-1.5-flash')
            resp = model.generate_content(prompt + "\nReturn JSON only.")
            cleaned = resp.text.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(cleaned)
        except Exception:
            raise RuntimeError(f"Error generating recipe: {str(e)}")

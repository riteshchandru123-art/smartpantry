import os
from datetime import datetime
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

import db
import ai_service

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="SmartPantry AI",
    page_icon="🥦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db.init_db()

# --- Custom Styling ---
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #e9ecef;
    }
    .warning-badge {
        background-color: #ffeaa7;
        color: #d63031;
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
    }
    .good-badge {
        background-color: #55efc4;
        color: #00b894;
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("🥦 SmartPantry AI")
    st.caption("Zero-Waste Smart Fridge Assistant")
    
    # API Key Handling
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "Google Gemini API Key",
        value=env_key,
        type="password",
        help="Get a free key at https://aistudio.google.com"
    )
    if api_key:
        st.session_state["api_key"] = api_key
        st.success("API Key configured!", icon="🔑")
    else:
        st.warning("Please provide a Gemini API Key to use Vision & Chef features.")

    st.divider()

    # Pantry Health Stats
    all_items = db.get_all_items()
    expiring_items = db.get_expiring_soon_items(days_ahead=3)
    
    col_stat1, col_stat2 = st.columns(2)
    col_stat1.metric("Total Items", len(all_items))
    col_stat2.metric("Expiring Soon", len(expiring_items), delta=-len(expiring_items) if expiring_items else 0, delta_color="inverse")

    st.divider()
    if st.button("🗑️ Clear Entire Pantry", use_container_width=True, type="secondary"):
        db.clear_all_items()
        st.rerun()

# --- Main App Header ---
st.header("🥗 Your Smart Kitchen Dashboard")

# --- Tabs ---
tab_scan, tab_inventory, tab_chef = st.tabs([
    "📸 Scan / Add Groceries",
    "🧺 Inventory & Expirations",
    "👨‍🍳 Zero-Waste AI Chef"
])

# ==========================================
# TAB 1: Scan & Add
# ==========================================
with tab_scan:
    st.subheader("Add Groceries to Your Pantry")
    scan_method = st.radio("Choose input method:", ["Upload Photo", "Take Photo with Camera", "Manual Entry"], horizontal=True)
    
    uploaded_image = None
    if scan_method == "Upload Photo":
        file = st.file_uploader("Upload fridge photo, vegetable shelf, or receipt", type=["jpg", "jpeg", "png", "webp"])
        if file:
            uploaded_image = Image.open(file)
            st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
    elif scan_method == "Take Photo with Camera":
        camera_file = st.camera_input("Snap a picture of your fridge or counter")
        if camera_file:
            uploaded_image = Image.open(camera_file)
    
    if uploaded_image is not None:
        if st.button("🔍 Analyze Ingredients with Gemini Vision", type="primary", use_container_width=True):
            current_key = st.session_state.get("api_key") or os.getenv("GEMINI_API_KEY")
            if not current_key:
                st.error("Please enter your Gemini API Key in the sidebar first!")
            else:
                with st.spinner("Gemini is inspecting your ingredients and estimating freshness..."):
                    try:
                        detected = ai_service.analyze_pantry_image(uploaded_image, api_key=current_key)
                        st.session_state["temp_detected"] = detected
                        st.success(f"Detected {len(detected)} items successfully!")
                    except Exception as e:
                        st.error(f"Vision analysis failed: {str(e)}")

    # Confirmation table for detected items
    if "temp_detected" in st.session_state and st.session_state["temp_detected"]:
        st.write("### Review Detected Items")
        items_to_save = []
        for i, item in enumerate(st.session_state["temp_detected"]):
            cols = st.columns([3, 2, 2, 2])
            name = cols[0].text_input("Item", value=item["name"], key=f"det_name_{i}")
            qty = cols[1].text_input("Quantity", value=item["quantity"], key=f"det_qty_{i}")
            cat = cols[2].selectbox("Category", ["Produce", "Dairy", "Meat/Protein", "Bakery", "Condiments", "Beverages", "Pantry", "Other"], 
                                    index=["Produce", "Dairy", "Meat/Protein", "Bakery", "Condiments", "Beverages", "Pantry", "Other"].index(item.get("category", "Other")) if item.get("category") in ["Produce", "Dairy", "Meat/Protein", "Bakery", "Condiments", "Beverages", "Pantry", "Other"] else 7,
                                    key=f"det_cat_{i}")
            exp = cols[3].text_input("Est. Expiry (YYYY-MM-DD)", value=item["expiry_date"], key=f"det_exp_{i}")
            items_to_save.append({"name": name, "quantity": qty, "category": cat, "expiry_date": exp, "notes": item.get("notes", "")})

        if st.button("✅ Confirm & Save All to Inventory", type="primary", use_container_width=True):
            for it in items_to_save:
                db.add_item(it["name"], it["quantity"], it["category"], it["expiry_date"], it["notes"])
            del st.session_state["temp_detected"]
            st.success("All items added to inventory!")
            st.rerun()

    if scan_method == "Manual Entry":
        with st.form("manual_add_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Item Name (e.g., Greek Yogurt, Avocados)")
            qty = col2.text_input("Quantity (e.g., 2 tubs, 500g)")
            
            col3, col4 = st.columns(2)
            cat = col3.selectbox("Category", ["Produce", "Dairy", "Meat/Protein", "Bakery", "Condiments", "Beverages", "Pantry", "Other"])
            exp_date = col4.date_input("Expiry Date", value=datetime.today())
            notes = st.text_input("Notes (optional)")
            
            submit = st.form_submit_button("Add Item to Pantry", type="primary")
            if submit:
                if name.strip():
                    db.add_item(name, qty, cat, exp_date.strftime("%Y-%m-%d"), notes)
                    st.success(f"Added {name} to inventory!")
                    st.rerun()
                else:
                    st.error("Item name is required.")

# ==========================================
# TAB 2: Inventory & Expiration Watchdog
# ==========================================
with tab_inventory:
    all_items = db.get_all_items()
    expiring_items = db.get_expiring_soon_items(days_ahead=3)
    
    if expiring_items:
        st.warning(f"⚠️ **Attention:** You have **{len(expiring_items)} item(s)** expiring within 3 days! Check the recipe tab to cook them today.")

    if not all_items:
        st.info("Your pantry is currently empty. Scan a photo or add items in the first tab!")
    else:
        # Category Filter
        categories = ["All"] + sorted(list({item["category"] for item in all_items}))
        selected_category = st.selectbox("Filter by Category", categories)

        filtered_items = all_items if selected_category == "All" else [it for it in all_items if it["category"] == selected_category]
        
        st.write(f"Showing **{len(filtered_items)}** items:")
        
        # Display as interactive cards
        today = datetime.now().date()
        for it in filtered_items:
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
            c1.markdown(f"**{it['name']}**")
            c2.caption(f"Qty: {it['quantity']}")
            c3.caption(f"📂 {it['category']}")
            
            if it["expiry_date"]:
                try:
                    exp_d = datetime.strptime(it["expiry_date"], "%Y-%m-%d").date()
                    delta = (exp_d - today).days
                    if delta < 0:
                        c4.markdown(f"<span class='warning-badge'>Expired {abs(delta)}d ago</span>", unsafe_allow_html=True)
                    elif delta <= 3:
                        c4.markdown(f"<span class='warning-badge'>Expires in {delta}d</span>", unsafe_allow_html=True)
                    else:
                        c4.markdown(f"<span class='good-badge'>Fresh ({delta}d left)</span>", unsafe_allow_html=True)
                except ValueError:
                    c4.caption(it["expiry_date"])
            else:
                c4.caption("No expiry date")

            if c5.button("❌", key=f"del_{it['id']}", help="Delete item"):
                db.delete_item(it['id'])
                st.rerun()
            st.divider()

# ==========================================
# TAB 3: Zero-Waste AI Chef
# ==========================================
with tab_chef:
    st.subheader("Zero-Waste Meal Generator")
    st.caption("AI crafts custom recipes specifically designed to use up your soon-to-expire groceries.")
    
    all_items = db.get_all_items()
    expiring_items = db.get_expiring_soon_items(days_ahead=3)
    
    if not all_items:
        st.info("Please add ingredients to your pantry before generating recipes.")
    else:
        col1, col2, col3 = st.columns(3)
        meal_type = col1.selectbox("Meal Type", ["Dinner", "Lunch", "Breakfast", "Snack", "Quick Stir-Fry / Bowl"])
        diet = col2.selectbox("Dietary Preference", ["None", "Vegetarian", "Vegan", "High-Protein", "Keto", "Gluten-Free"])
        max_time = col3.slider("Max Cooking Time (minutes)", 10, 60, 30, step=5)
        
        if expiring_items:
            st.info(f"Targeting **{len(expiring_items)} expiring items**: " + ", ".join([it['name'] for it in expiring_items]))

        if st.button("🍳 Generate Zero-Waste Recipe", type="primary", use_container_width=True):
            current_key = st.session_state.get("api_key") or os.getenv("GEMINI_API_KEY")
            if not current_key:
                st.error("Please enter your Gemini API Key in the sidebar.")
            else:
                with st.spinner("AI Chef is combining your ingredients into a delicious zero-waste meal..."):
                    try:
                        recipe = ai_service.generate_recipe(
                            available_items=all_items,
                            expiring_soon_items=expiring_items,
                            dietary_preferences=diet,
                            meal_type=meal_type,
                            max_time_minutes=max_time,
                            api_key=current_key
                        )
                        st.session_state["current_recipe"] = recipe
                    except Exception as e:
                        st.error(f"Recipe generation error: {str(e)}")

        if "current_recipe" in st.session_state:
            rc = st.session_state["current_recipe"]
            st.markdown(f"## 🍽️ {rc.get('title', 'Chef Recipe')}")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Prep Time", f"{rc.get('prep_time_minutes', 10)} mins")
            m2.metric("Cook Time", f"{rc.get('cook_time_minutes', 20)} mins")
            m3.metric("Servings", rc.get('servings', 2))
            
            st.success(f"🌱 **Zero-Waste Impact:** {rc.get('zero_waste_tip', 'Maximizes pantry efficiency.')}")
            
            col_ing1, col_ing2 = st.columns(2)
            with col_ing1:
                st.markdown("### 🛒 From Your Pantry")
                for ing in rc.get("ingredients_used", []):
                    st.markdown(f"- ✅ {ing}")
            
            with col_ing2:
                st.markdown("### 🧂 Staples / Additional")
                for add in rc.get("additional_needed", []):
                    st.markdown(f"- 🔸 {add}")
                    
            st.markdown("### 📋 Instructions")
            for step in rc.get("instructions", []):
                st.markdown(f"1. {step}")

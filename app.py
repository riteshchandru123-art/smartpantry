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
    page_title="SmartPantry Pro | NutriWallet",
    page_icon="🥦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database with new migrations
db.init_db()

# --- Custom Styling ---
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .savings-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 700;
        display: inline-block;
    }
    .macro-badge {
        background-color: #cce5ff;
        color: #004085;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .warning-badge {
        background-color: #ffeaa7;
        color: #d63031;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: bold;
    }
    .good-badge {
        background-color: #55efc4;
        color: #00b894;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Helper for Plotly Charts
def render_macro_donut(protein_g: float, carbs_g: float, fat_g: float, title: str = "Macronutrient Split"):
    try:
        import plotly.graph_objects as go
        labels = ['Protein (g)', 'Carbs (g)', 'Fat (g)']
        values = [protein_g, carbs_g, fat_g]
        colors = ['#3498db', '#2ecc71', '#e67e22']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.6,
            marker=dict(colors=colors),
            textinfo='label+percent',
            hoverinfo='label+value'
        )])
        fig.update_layout(
            title=title,
            showlegend=False,
            margin=dict(t=35, b=10, l=10, r=10),
            height=220
        )
        return fig
    except Exception:
        return None

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("🥦 NutriWallet AI")
    st.caption("Precision Macros • Zero-Waste • Wallet Savings")
    
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
        st.success("API Key Active", icon="🔑")
    else:
        st.warning("Enter Gemini API Key to enable Vision & AI Chef.")

    st.divider()

    # Financial & Inventory Metrics
    all_items = db.get_all_items()
    expiring_items = db.get_expiring_soon_items(days_ahead=3)
    total_val = db.get_total_inventory_value()
    today_stats = db.get_today_nutrition_summary()

    st.markdown("### 📊 Live Health & Wallet Tracker")
    c_side1, c_side2 = st.columns(2)
    c_side1.metric("Pantry Value", f"${total_val:.2f}")
    c_side2.metric("Saved Today", f"+${today_stats['savings']:.2f}")

    col_side3, col_side4 = st.columns(2)
    col_side3.metric("Items in Stock", len(all_items))
    col_side4.metric("Expiring Soon", len(expiring_items), delta=-len(expiring_items) if expiring_items else 0, delta_color="inverse")

    st.divider()
    if st.button("🗑️ Clear Entire Pantry", use_container_width=True, type="secondary"):
        db.clear_all_items()
        st.rerun()

# --- Main App Header & Daily Tracker ---
st.markdown("# 🥗 NutriWallet: Smart Pantry & Fitness Engine")
st.caption("Hit your daily macro targets and track real cash saved by cooking what is already in your fridge.")

# Today's Progress Banner
if today_stats["meals_count"] > 0:
    st.markdown("### 🏆 Today's Progress")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Meals Cooked", today_stats["meals_count"])
    m2.metric("Protein Logged", f"{today_stats['protein_g']}g")
    m3.metric("Calories", f"{today_stats['calories']} kcal")
    m4.metric("Money Saved", f"${today_stats['savings']:.2f}")
    m5.metric("Cost to Cook", f"${today_stats['cost']:.2f}")
    
    macro_chart = render_macro_donut(today_stats['protein_g'], today_stats['carbs_g'], today_stats['fat_g'], "Today's Macro Ratio")
    if macro_chart:
        st.plotly_chart(macro_chart, use_container_width=True)
    st.divider()

# --- Tabs ---
tab_scan, tab_inventory, tab_chef = st.tabs([
    "📸 Smart Scan (Fridge / Receipt)",
    "🧺 Pantry & Value Vault",
    "🏋️‍♂️💸 NutriWallet AI Chef"
])

# ==========================================
# TAB 1: Smart Scan (Fridge & Receipts)
# ==========================================
with tab_scan:
    st.subheader("Dual-Vision Intake: Fridge Photo or Supermarket Receipt")
    scan_type = st.radio("What are you scanning?", ["📸 Fridge / Pantry Shelves", "🧾 Supermarket Paper Receipt", "✍️ Manual Entry"], horizontal=True)
    
    uploaded_image = None
    if scan_type in ["📸 Fridge / Pantry Shelves", "🧾 Supermarket Paper Receipt"]:
        input_source = st.radio("Source:", ["Upload Image File", "Use Laptop/Phone Camera"], horizontal=True)
        if input_source == "Upload Image File":
            file = st.file_uploader("Upload JPG, PNG or WEBP", type=["jpg", "jpeg", "png", "webp"])
            if file:
                uploaded_image = Image.open(file)
                st.image(uploaded_image, caption="Uploaded Preview", use_container_width=True)
        else:
            cam_file = st.camera_input("Capture with Camera")
            if cam_file:
                uploaded_image = Image.open(cam_file)

    if uploaded_image is not None:
        button_label = "🔍 Parse Supermarket Receipt with OCR" if "Receipt" in scan_type else "🔍 Analyze Fridge Ingredients & Macros"
        if st.button(button_label, type="primary", use_container_width=True):
            current_key = st.session_state.get("api_key") or os.getenv("GEMINI_API_KEY")
            if not current_key:
                st.error("Please enter your Gemini API Key in the sidebar first!")
            else:
                with st.spinner("Gemini is reading items, prices, and nutritional profiles..."):
                    try:
                        if "Receipt" in scan_type:
                            res = ai_service.analyze_receipt_image(uploaded_image, api_key=current_key)
                            st.session_state["temp_detected"] = res.get("items", [])
                            st.success(f"Receipt from '{res.get('store_name', 'Store')}' parsed! Total: ${res.get('total_spent', 0.0):.2f}")
                        else:
                            detected = ai_service.analyze_pantry_image(uploaded_image, api_key=current_key)
                            st.session_state["temp_detected"] = detected
                            st.success(f"Detected {len(detected)} items with macros and estimated prices!")
                    except Exception as e:
                        st.error(f"Scan analysis failed: {str(e)}")

    # Confirmation & Review Table
    if "temp_detected" in st.session_state and st.session_state["temp_detected"]:
        st.write("### 🛒 Review & Save Detected Groceries")
        items_to_save = []
        for i, item in enumerate(st.session_state["temp_detected"]):
            cols = st.columns([3, 2, 2, 2, 2])
            name = cols[0].text_input("Item", value=item["name"], key=f"it_name_{i}")
            qty = cols[1].text_input("Quantity", value=item["quantity"], key=f"it_qty_{i}")
            price = cols[2].number_input("Price ($)", value=float(item.get("price", 2.50)), step=0.5, key=f"it_prc_{i}")
            prot = cols[3].number_input("Protein (g)", value=float(item.get("protein_g", 5.0)), step=1.0, key=f"it_prt_{i}")
            exp = cols[4].text_input("Expiry (YYYY-MM-DD)", value=item["expiry_date"], key=f"it_exp_{i}")
            
            items_to_save.append({
                "name": name,
                "quantity": qty,
                "category": item.get("category", "Other"),
                "expiry_date": exp,
                "price": price,
                "calories": item.get("calories", 100),
                "protein_g": prot,
                "carbs_g": item.get("carbs_g", 10.0),
                "fat_g": item.get("fat_g", 2.0),
                "notes": item.get("notes", "")
            })

        if st.button("✅ Confirm & Save All to Inventory", type="primary", use_container_width=True):
            for it in items_to_save:
                db.add_item(
                    name=it["name"],
                    quantity=it["quantity"],
                    category=it["category"],
                    expiry_date=it["expiry_date"],
                    notes=it["notes"],
                    price=it["price"],
                    calories=it["calories"],
                    protein_g=it["protein_g"],
                    carbs_g=it["carbs_g"],
                    fat_g=it["fat_g"]
                )
            del st.session_state["temp_detected"]
            st.success("All items saved to inventory!")
            st.rerun()

    if scan_type == "✍️ Manual Entry":
        with st.form("manual_entry_form"):
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Item Name (e.g., Chicken Breast, Oats)")
            qty = c2.text_input("Quantity (e.g., 500g, 1 carton)")
            price = c3.number_input("Price ($)", value=3.99, step=0.5)
            
            c4, c5, c6 = st.columns(3)
            category = c4.selectbox("Category", ["Meat/Protein", "Produce", "Dairy", "Bakery", "Condiments", "Beverages", "Pantry", "Other"])
            protein = c5.number_input("Est. Protein (grams)", value=25.0, step=1.0)
            exp_date = c6.date_input("Expiry Date", value=datetime.today())

            submit = st.form_submit_button("Add Item", type="primary")
            if submit:
                if name.strip():
                    db.add_item(
                        name=name,
                        quantity=qty,
                        category=category,
                        expiry_date=exp_date.strftime("%Y-%m-%d"),
                        price=price,
                        protein_g=protein
                    )
                    st.success(f"Added {name}!")
                    st.rerun()
                else:
                    st.error("Name is required.")

# ==========================================
# TAB 2: Pantry & Value Vault
# ==========================================
with tab_inventory:
    all_items = db.get_all_items()
    expiring_items = db.get_expiring_soon_items(days_ahead=3)
    
    if expiring_items:
        st.warning(f"⚠️ **Urgent:** You have **{len(expiring_items)} item(s)** expiring within 3 days! Check the Chef tab to cook them before money goes to waste.")

    if not all_items:
        st.info("Your pantry is empty. Use the Smart Scan tab to add items from photos or receipts!")
    else:
        cat_list = ["All"] + sorted(list({item["category"] for item in all_items}))
        selected_cat = st.selectbox("Filter by Category", cat_list)
        filtered = all_items if selected_cat == "All" else [it for it in all_items if it["category"] == selected_cat]

        st.write(f"Showing **{len(filtered)}** items (Total Value: **${sum(it.get('price', 0) for it in filtered):.2f}**):")
        
        today = datetime.now().date()
        for it in filtered:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
            col1.markdown(f"**{it['name']}**")
            col2.caption(f"Qty: {it['quantity']} • 💲**${it.get('price', 0.0):.2f}**")
            col3.markdown(f"<span class='macro-badge'>💪 {it.get('protein_g', 0)}g Protein</span>", unsafe_allow_html=True)
            
            if it["expiry_date"]:
                try:
                    exp_d = datetime.strptime(it["expiry_date"], "%Y-%m-%d").date()
                    delta = (exp_d - today).days
                    if delta < 0:
                        col4.markdown(f"<span class='warning-badge'>Expired {abs(delta)}d ago</span>", unsafe_allow_html=True)
                    elif delta <= 3:
                        col4.markdown(f"<span class='warning-badge'>Expires in {delta}d</span>", unsafe_allow_html=True)
                    else:
                        col4.markdown(f"<span class='good-badge'>Fresh ({delta}d)</span>", unsafe_allow_html=True)
                except ValueError:
                    col4.caption(it["expiry_date"])
            else:
                col4.caption("No expiry date")

            if col5.button("❌", key=f"del_{it['id']}", help="Delete item"):
                db.delete_item(it['id'])
                st.rerun()
            st.divider()

# ==========================================
# TAB 3: NutriWallet AI Chef
# ==========================================
with tab_chef:
    st.subheader("🏋️‍♂️ Precision Macro & Wallet-Saver Recipe Generator")
    st.caption("Generates meals designed to hit your exact fitness targets while calculating how much money you save vs. takeout.")
    
    all_items = db.get_all_items()
    expiring_items = db.get_expiring_soon_items(days_ahead=3)
    
    if not all_items:
        st.info("Please add ingredients to your pantry before synthesizing meals.")
    else:
        # Fitness & Budget Goal Controls
        col_g1, col_g2, col_g3 = st.columns(3)
        goal_preset = col_g1.selectbox(
            "Fitness Objective", 
            ["High-Protein Cut (Fat Loss)", "Lean Muscle Bulk", "Keto / Low-Carb", "Budget Minimalist", "Endurance / Carb-Fuel"]
        )
        meal_type = col_g2.selectbox("Meal Type", ["Dinner", "Lunch", "Post-Workout Meal", "Breakfast", "Quick Bowl"])
        max_time = col_g3.slider("Max Cooking Time (mins)", 10, 60, 25, step=5)

        col_t1, col_t2 = st.columns(2)
        target_protein = col_t1.slider("Target Protein per Serving (grams)", 15, 80, 40, step=5)
        target_cals = col_t2.slider("Target Calories per Serving (kcal)", 250, 1000, 500, step=50)

        if expiring_items:
            st.info(f"Targeting **{len(expiring_items)} expiring items**: " + ", ".join([it['name'] for it in expiring_items]))

        if st.button("🍳 Synthesize Macro & Budget Recipe", type="primary", use_container_width=True):
            current_key = st.session_state.get("api_key") or os.getenv("GEMINI_API_KEY")
            if not current_key:
                st.error("Please enter your Gemini API Key in the sidebar.")
            else:
                with st.spinner("AI Chef & Sports Nutritionist is formulating your optimal recipe..."):
                    try:
                        recipe = ai_service.generate_recipe(
                            available_items=all_items,
                            expiring_soon_items=expiring_items,
                            fitness_goal=goal_preset,
                            target_protein_g=target_protein,
                            target_calories=target_cals,
                            meal_type=meal_type,
                            max_time_minutes=max_time,
                            api_key=current_key
                        )
                        st.session_state["current_recipe"] = recipe
                    except Exception as e:
                        st.error(f"Recipe generation error: {str(e)}")

        # Render Generated Recipe
        if "current_recipe" in st.session_state:
            rc = st.session_state["current_recipe"]
            cost = rc.get("cost_analysis", {})
            nutr = rc.get("nutritional_profile", {})
            
            st.markdown(f"## 🍽️ {rc.get('title', 'Chef Recipe')}")
            st.caption(f"⏱️ Prep: {rc.get('prep_time_minutes', 10)} mins | Cook: {rc.get('cook_time_minutes', 15)} mins | Servings: {rc.get('servings', 2)}")

            # --- Financial & Savings Banner ---
            st.markdown("### 💸 Cost & Takeout Comparison")
            c_cost1, c_cost2, c_cost3, c_cost4 = st.columns(4)
            c_cost1.metric("Home Cook Cost", f"${cost.get('cost_to_cook_per_serving', 2.50):.2f}")
            c_cost2.metric("Takeout Equivalent", f"${cost.get('takeout_equivalent_cost', 15.00):.2f}")
            c_cost3.metric("Money Saved / Plate", f"+${cost.get('money_saved_per_serving', 12.50):.2f}", delta="Saved")
            c_cost4.metric("Protein Efficiency", f"${cost.get('cost_per_gram_protein', 0.06):.2f}/g")

            st.markdown(f"<span class='savings-badge'>🎉 You save approx ${cost.get('money_saved_per_serving', 12.0) * rc.get('servings', 2):.2f} total compared to DoorDash/takeout!</span>", unsafe_allow_html=True)
            st.write("")

            # --- Macro Breakdown & Donut Chart ---
            st.markdown("### 🏋️‍♂️ Macronutrient Profile (Per Serving)")
            cm1, cm2 = st.columns([2, 3])
            with cm1:
                st.metric("Calories", f"{nutr.get('calories', 500)} kcal")
                st.metric("Protein", f"{nutr.get('protein_g', 40)}g")
                st.metric("Carbohydrates", f"{nutr.get('carbs_g', 45)}g")
                st.metric("Healthy Fats", f"{nutr.get('fat_g', 15)}g")
                if rc.get("macro_alignment_tip"):
                    st.info(f"💡 {rc.get('macro_alignment_tip')}")

            with cm2:
                pie = render_macro_donut(
                    nutr.get('protein_g', 40),
                    nutr.get('carbs_g', 45),
                    nutr.get('fat_g', 15),
                    "Per Serving Macro Split"
                )
                if pie:
                    st.plotly_chart(pie, use_container_width=True)

            # --- Ingredients & Instructions ---
            st.divider()
            ci1, ci2 = st.columns(2)
            with ci1:
                st.markdown("### 🛒 Ingredients From Your Pantry")
                for ing in rc.get("ingredients_used", []):
                    st.markdown(f"- ✅ {ing}")
            with ci2:
                st.markdown("### 🧂 Staples / Additional")
                for add in rc.get("additional_needed", []):
                    st.markdown(f"- 🔸 {add}")

            st.markdown("### 📋 Step-by-Step Instructions")
            for step in rc.get("instructions", []):
                st.markdown(f"1. {step}")

            if rc.get("zero_waste_tip"):
                st.success(f"🌱 **Zero-Waste Impact:** {rc.get('zero_waste_tip')}")

            # --- Log Meal Action ---
            st.divider()
            if st.button("✅ I Cooked This Meal! (Log to Today's Health & Wallet Tracker)", type="primary", use_container_width=True):
                db.log_meal(
                    recipe_title=rc.get("title", "NutriWallet Meal"),
                    calories=int(nutr.get("calories", 0)),
                    protein_g=float(nutr.get("protein_g", 0.0)),
                    carbs_g=float(nutr.get("carbs_g", 0.0)),
                    fat_g=float(nutr.get("fat_g", 0.0)),
                    cost=float(cost.get("cost_to_cook_per_serving", 0.0)),
                    takeout_savings=float(cost.get("money_saved_per_serving", 0.0))
                )
                st.balloons()
                st.success("Meal logged to your daily tracker! Check your dashboard progress at the top.")
                st.rerun()

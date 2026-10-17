import os
from datetime import datetime
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

import importlib
import db
import ai_service
importlib.reload(ai_service)

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="NutriWallet AI • Smart Kitchen",
    page_icon="🥑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db.init_db()

# --- High-End CSS Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hero Header */
    .hero-banner {
        background: linear-gradient(135deg, #091e3a 0%, #102a45 40%, #064e3b 100%);
        border-radius: 20px;
        padding: 32px 36px;
        color: white;
        margin-bottom: 28px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.12);
        position: relative;
        overflow: hidden;
    }
    .hero-banner h1 {
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
        margin-bottom: 8px !important;
        background: linear-gradient(90deg, #ffffff 0%, #a7f3d0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-banner p {
        font-size: 1.05rem;
        color: #cbd5e1;
        margin-bottom: 0;
        max-width: 750px;
    }
    .hero-pill {
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        color: #6ee7b7;
        border: 1px solid rgba(110, 231, 183, 0.3);
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }

    /* KPI / Stat Cards */
    .kpi-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 20px 22px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(6, 78, 59, 0.08);
        border-color: #cbd5e1;
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #10b981, #06b6d4);
    }
    .kpi-label {
        font-size: 0.82rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .kpi-val {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.82rem;
        color: #10b981;
        font-weight: 600;
        margin-top: 6px;
    }

    /* Food Item Card */
    .food-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 16px 20px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s ease;
    }
    .food-card:hover {
        border-color: #cbd5e1;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
    }

    /* Badges */
    .tag-macro {
        background: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .tag-price {
        background: #eff6ff;
        color: #1e40af;
        border: 1px solid #bfdbfe;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 8px;
    }
    .tag-urgency-danger {
        background: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 8px;
    }
    .tag-urgency-warning {
        background: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 8px;
    }
    .tag-urgency-good {
        background: #f0fdf4;
        color: #15803d;
        border: 1px solid #bbf7d0;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 8px;
    }

    /* Savings Hero Card */
    .savings-showcase {
        background: linear-gradient(135deg, #052e16 0%, #14532d 100%);
        border-radius: 16px;
        padding: 24px 28px;
        color: white;
        margin: 20px 0;
        border: 1px solid #22c55e40;
        box-shadow: 0 10px 25px rgba(20, 83, 45, 0.2);
    }
    .savings-showcase h3 {
        color: #86efac !important;
        font-weight: 800;
        margin-bottom: 4px;
        font-size: 1.4rem;
    }

    /* Recipe Step List */
    .step-box {
        background: #f8fafc;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        border-left: 4px solid #10b981;
        font-size: 0.95rem;
        line-height: 1.5;
        color: #334155;
    }

    /* Hide Streamlit default branding watermark */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Helper for Plotly Charts
def render_macro_donut(protein_g: float, carbs_g: float, fat_g: float, title: str = "Macronutrient Split"):
    try:
        import plotly.graph_objects as go
        labels = ['Protein', 'Carbohydrates', 'Healthy Fats']
        values = [max(protein_g, 0.1), max(carbs_g, 0.1), max(fat_g, 0.1)]
        colors = ['#10b981', '#0ea5e9', '#f59e0b']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.65,
            marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
            textinfo='percent+label',
            hoverinfo='label+value',
            textposition='outside'
        )])
        fig.update_layout(
            title=dict(text=f"<b>{title}</b>", font=dict(size=14, color="#334155", family="Plus Jakarta Sans")),
            showlegend=False,
            margin=dict(t=40, b=15, l=15, r=15),
            height=240,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    except Exception:
        return None

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 10px 0;'>
            <div style='font-size: 2.8rem;'>🥑</div>
            <h2 style='margin: 0; font-weight: 800; font-size: 1.5rem; color: #0f172a;'>NutriWallet</h2>
            <p style='color: #64748b; font-size: 0.85rem; margin-top: 2px;'>AI Precision Macros & Budget Engine</p>
        </div>
    """, unsafe_allow_html=True)
    
    # API Key Input with clean badge
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "🔑 Gemini API Key",
        value=env_key,
        type="password",
        help="Free key from https://aistudio.google.com"
    )
    if api_key:
        st.session_state["api_key"] = api_key
        st.markdown("<span class='tag-urgency-good'>● AI Engine Online</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='tag-urgency-danger'>● Missing API Key</span>", unsafe_allow_html=True)

    st.divider()

    # Sidebar Quick Stats
    all_items = db.get_all_items()
    expiring_items = db.get_expiring_soon_items(days_ahead=3)
    total_val = db.get_total_inventory_value()
    today_stats = db.get_today_nutrition_summary()

    st.markdown("#### ⚡ Quick Overview")
    sc1, sc2 = st.columns(2)
    sc1.metric("Stocked", f"{len(all_items)} items")
    sc2.metric("Pantry Value", f"${total_val:.2f}")

    if expiring_items:
        st.markdown(f"<div style='background: #fff1f2; border: 1px solid #fecdd3; padding: 10px 14px; border-radius: 10px; color: #9f1239; font-size: 0.82rem; font-weight: 700; margin: 10px 0;'>⚠️ {len(expiring_items)} item(s) expiring within 3 days!</div>", unsafe_allow_html=True)

    st.divider()
    if st.button("🗑️ Reset Pantry Database", use_container_width=True, type="secondary"):
        db.clear_all_items()
        st.rerun()

# --- Top Hero Banner ---
st.markdown("""
<div class="hero-banner">
    <div class="hero-pill">⚡ Precision Macros • Zero-Waste • Wallet Savings</div>
    <h1>Eat Like an Athlete. Save Like an Investor.</h1>
    <p>Snap your fridge or grocery receipts. Our multimodal AI optimizes your daily protein and calories while slashing food waste and calculating money saved vs. takeout.</p>
</div>
""", unsafe_allow_html=True)

# --- Real-Time KPI Cards ---
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">💰 Money Saved Today</div>
        <div class="kpi-val">+${today_stats['savings']:.2f}</div>
        <div class="kpi-sub">vs. Restaurant Takeout</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">💪 Protein Logged</div>
        <div class="kpi-val">{today_stats['protein_g']:.0f}g</div>
        <div class="kpi-sub">{today_stats['calories']} Total kcal</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">🍳 Meals Prepared</div>
        <div class="kpi-val">{today_stats['meals_count']}</div>
        <div class="kpi-sub">${today_stats['cost']:.2f} Home Cost</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">🧊 Fridge Inventory</div>
        <div class="kpi-val">${total_val:.2f}</div>
        <div class="kpi-sub">{len(all_items)} Items Active</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Today's Progress Chart (If meals are logged)
if today_stats["meals_count"] > 0:
    with st.expander("📊 View Today's Nutritional Breakdown", expanded=True):
        chart_c1, chart_c2 = st.columns([1, 2])
        with chart_c1:
            donut = render_macro_donut(today_stats['protein_g'], today_stats['carbs_g'], today_stats['fat_g'], "Today's Macro Ratio")
            if donut:
                st.plotly_chart(donut, use_container_width=True)
        with chart_c2:
            st.markdown(f"""
            <div style='padding: 20px;'>
                <h4 style='color: #0f172a; margin-bottom: 12px;'>🎯 Daily Nutrition Summary</h4>
                <p style='color: #64748b; margin-bottom: 8px;'><b>Protein:</b> <span style='color: #10b981; font-weight: 700;'>{today_stats['protein_g']}g</span></p>
                <p style='color: #64748b; margin-bottom: 8px;'><b>Carbohydrates:</b> <span style='color: #0ea5e9; font-weight: 700;'>{today_stats['carbs_g']}g</span></p>
                <p style='color: #64748b; margin-bottom: 8px;'><b>Healthy Fats:</b> <span style='color: #f59e0b; font-weight: 700;'>{today_stats['fat_g']}g</span></p>
                <p style='color: #64748b;'><b>Total Energy:</b> <span style='color: #334155; font-weight: 700;'>{today_stats['calories']} kcal</span></p>
            </div>
            """, unsafe_allow_html=True)

# --- Main Application Tabs ---
tab_scan, tab_inventory, tab_chef = st.tabs([
    "📸 Vision Scanner & Receipt OCR",
    "🧺 Inventory & Value Vault",
    "👨‍🍳💸 NutriWallet AI Chef"
])

# ==========================================
# TAB 1: Smart Scanner (Fridge / Receipt)
# ==========================================
with tab_scan:
    st.markdown("### 📷 Multimodal Smart Intake")
    st.caption("Upload a fridge photo to auto-detect ingredients and macros, or a paper receipt to extract itemized costs.")
    
    col_input1, col_input2 = st.columns([1, 2])
    with col_input1:
        scan_mode = st.radio(
            "Scan Type:",
            ["🧊 Fridge / Pantry Photo", "🧾 Supermarket Receipt", "✍️ Manual Entry"],
            help="Receipts extract exact prices; Fridge photos estimate macros & shelf life."
        )
        if scan_mode != "✍️ Manual Entry":
            source_type = st.radio("Capture Method:", ["📁 Upload File", "📷 Live Camera"], horizontal=True)

    uploaded_image = None
    with col_input2:
        if scan_mode != "✍️ Manual Entry":
            if source_type == "📁 Upload File":
                img_file = st.file_uploader("Drop image here (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])
                if img_file:
                    uploaded_image = Image.open(img_file)
                    st.image(uploaded_image, caption="Preview", use_container_width=True)
            else:
                cam_snap = st.camera_input("Take photo")
                if cam_snap:
                    uploaded_image = Image.open(cam_snap)

    if uploaded_image is not None:
        action_btn_text = "🧾 Extract Receipt Items & Prices with OCR" if "Receipt" in scan_mode else "🔍 Analyze Fridge Ingredients & Macros"
        if st.button(action_btn_text, type="primary", use_container_width=True):
            current_key = st.session_state.get("api_key") or os.getenv("GEMINI_API_KEY")
            if not current_key:
                st.error("Please provide your Gemini API Key in the sidebar first!")
            else:
                with st.spinner("🤖 Gemini Multimodal AI is processing visual details..."):
                    try:
                        if "Receipt" in scan_mode:
                            parsed_data = ai_service.analyze_receipt_image(uploaded_image, api_key=current_key)
                            st.session_state["temp_detected"] = parsed_data.get("items", [])
                            st.success(f"Receipt from '{parsed_data.get('store_name', 'Supermarket')}' parsed! Total: ${parsed_data.get('total_spent', 0.0):.2f}")
                        else:
                            detected_items = ai_service.analyze_pantry_image(uploaded_image, api_key=current_key)
                            st.session_state["temp_detected"] = detected_items
                            st.success(f"Identified {len(detected_items)} items with estimated protein and freshness windows!")
                    except Exception as e:
                        st.error(f"Vision analysis failed: {str(e)}")

    # Review & Confirm Table
    if "temp_detected" in st.session_state and st.session_state["temp_detected"]:
        st.markdown("---")
        st.markdown("### 🛒 Review & Save Detected Items")
        items_to_save = []
        for i, item in enumerate(st.session_state["temp_detected"]):
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
            name = c1.text_input("Item Name", value=item["name"], key=f"t_name_{i}")
            qty = c2.text_input("Qty", value=item["quantity"], key=f"t_qty_{i}")
            price = c3.number_input("Price ($)", value=float(item.get("price", 2.50)), step=0.25, key=f"t_prc_{i}")
            prot = c4.number_input("Protein (g)", value=float(item.get("protein_g", 5.0)), step=1.0, key=f"t_prot_{i}")
            exp = c5.text_input("Expiry (YYYY-MM-DD)", value=item["expiry_date"], key=f"t_exp_{i}")
            
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

        if st.button("💾 Save All Items to Inventory", type="primary", use_container_width=True):
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
            st.toast("Groceries saved to inventory successfully!", icon="✅")
            st.rerun()

    if scan_mode == "✍️ Manual Entry":
        with st.form("manual_add_form"):
            st.markdown("#### Quick Add Form")
            m_c1, m_c2, m_c3 = st.columns(3)
            name = m_c1.text_input("Item Name (e.g. Greek Yogurt, Eggs, Tofu)")
            qty = m_c2.text_input("Quantity (e.g. 500g, 6 pack)")
            price = m_c3.number_input("Price ($)", value=3.49, step=0.5)

            m_c4, m_c5, m_c6 = st.columns(3)
            category = m_c4.selectbox("Category", ["Meat/Protein", "Produce", "Dairy", "Bakery", "Condiments", "Beverages", "Pantry", "Other"])
            protein = m_c5.number_input("Protein (grams)", value=20.0, step=1.0)
            exp_date = m_c6.date_input("Expiry Date", value=datetime.today())

            if st.form_submit_button("Add to Pantry", type="primary"):
                if name.strip():
                    db.add_item(
                        name=name,
                        quantity=qty,
                        category=category,
                        expiry_date=exp_date.strftime("%Y-%m-%d"),
                        price=price,
                        protein_g=protein
                    )
                    st.toast(f"Added {name}!", icon="🥑")
                    st.rerun()
                else:
                    st.error("Name is required.")

# ==========================================
# TAB 2: Inventory & Value Vault
# ==========================================
with tab_inventory:
    all_items = db.get_all_items()
    expiring_items = db.get_expiring_soon_items(days_ahead=3)
    
    col_filter1, col_filter2 = st.columns([2, 1])
    with col_filter1:
        cat_choices = ["All Categories"] + sorted(list({it["category"] for it in all_items}))
        selected_category = st.selectbox("Filter by Category", cat_choices)
    with col_filter2:
        st.write("")
        st.write("")
        st.markdown(f"**Total Pantry Assets:** <span class='tag-price'>${total_val:.2f}</span>", unsafe_allow_html=True)

    filtered_items = all_items if selected_category == "All Categories" else [it for it in all_items if it["category"] == selected_category]

    if not filtered_items:
        st.info("No items in this category. Add groceries via the Vision Scanner tab!")
    else:
        today = datetime.now().date()
        for it in filtered_items:
            # Urgency status styling
            urgency_html = "<span class='tag-urgency-good'>Fresh</span>"
            if it["expiry_date"]:
                try:
                    exp_d = datetime.strptime(it["expiry_date"], "%Y-%m-%d").date()
                    delta = (exp_d - today).days
                    if delta < 0:
                        urgency_html = f"<span class='tag-urgency-danger'>⚠️ Expired {abs(delta)}d ago</span>"
                    elif delta <= 3:
                        urgency_html = f"<span class='tag-urgency-warning'>⏳ Expires in {delta}d</span>"
                    else:
                        urgency_html = f"<span class='tag-urgency-good'>Fresh ({delta}d left)</span>"
                except ValueError:
                    urgency_html = f"<span>{it['expiry_date']}</span>"

            # Render custom sleek food row
            f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns([3, 2, 2, 2, 1])
            f_col1.markdown(f"**{it['name']}**<br><span style='color: #64748b; font-size: 0.8rem;'>{it['quantity']} • {it['category']}</span>", unsafe_allow_html=True)
            f_col2.markdown(f"<span class='tag-price'>💲 ${it.get('price', 0.0):.2f}</span>", unsafe_allow_html=True)
            f_col3.markdown(f"<span class='tag-macro'>💪 {it.get('protein_g', 0):.0f}g Protein</span>", unsafe_allow_html=True)
            f_col4.markdown(urgency_html, unsafe_allow_html=True)
            
            if f_col5.button("🗑️", key=f"del_item_{it['id']}", help="Delete item"):
                db.delete_item(it['id'])
                st.rerun()
            st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #f1f5f9;'/>", unsafe_allow_html=True)

# ==========================================
# TAB 3: NutriWallet AI Chef
# ==========================================
with tab_chef:
    st.markdown("### 👨‍🍳 Precision Macro & Budget Recipe Synthesizer")
    st.caption("AI calculates the exact ingredient portions to hit your target calories and protein while maximizing takeout savings.")

    if not all_items:
        st.info("Your pantry is currently empty. Please add items in the Scanner tab first!")
    else:
        # Settings Bar
        cfg_c1, cfg_c2, cfg_c3 = st.columns(3)
        with cfg_c1:
            goal_preset = st.selectbox(
                "🎯 Fitness Goal",
                ["High-Protein Cut (Fat Loss)", "Lean Muscle Bulk", "Keto / Low-Carb", "Budget Minimalist", "Endurance / Carb-Fuel"]
            )
        with cfg_c2:
            meal_kind = st.selectbox("🍽️ Meal Type", ["Dinner", "Post-Workout Lunch", "High-Protein Breakfast", "Quick Stir-Fry Bowl"])
        with cfg_c3:
            max_cook_time = st.slider("⏱️ Max Cooking Time", 10, 60, 25, step=5)

        tar_c1, tar_c2 = st.columns(2)
        with tar_c1:
            target_protein = st.slider("Target Protein / Serving", 15, 80, 42, step=1, format="%d g")
        with tar_c2:
            target_calories = st.slider("Target Calories / Serving", 250, 1000, 520, step=25, format="%d kcal")

        if expiring_items:
            st.markdown(f"""
            <div style='background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 10px 14px; color: #92400e; font-size: 0.88rem; margin: 12px 0;'>
                🥦 <b>Expiring Ingredients Targeted:</b> {', '.join([it['name'] for it in expiring_items])}
            </div>
            """, unsafe_allow_html=True)

        if st.button("🚀 Synthesize Targeted Recipe & Calculate Savings", type="primary", use_container_width=True):
            current_key = st.session_state.get("api_key") or os.getenv("GEMINI_API_KEY")
            if not current_key:
                st.error("Please enter your Gemini API Key in the sidebar.")
            else:
                with st.spinner("🧑‍🍳 Formulating recipe, calculating cost-per-plate, and verifying macronutrients..."):
                    try:
                        recipe = ai_service.generate_recipe(
                            available_items=all_items,
                            expiring_soon_items=expiring_items,
                            fitness_goal=goal_preset,
                            target_protein_g=target_protein,
                            target_calories=target_calories,
                            meal_type=meal_kind,
                            max_time_minutes=max_cook_time,
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
            
            st.markdown("---")
            st.markdown(f"# 🍽️ {rc.get('title', 'Chef Creation')}")
            st.markdown(f"""
                <span class='tag-macro'>⏱️ {rc.get('prep_time_minutes', 10) + rc.get('cook_time_minutes', 15)} Mins Total</span>
                <span class='tag-macro'>👥 {rc.get('servings', 2)} Servings</span>
                <span class='tag-macro'>💪 {nutr.get('protein_g', 40)}g Protein</span>
                <span class='tag-price'>💰 ${cost.get('cost_to_cook_per_serving', 2.50):.2f} / Plate</span>
            """, unsafe_allow_html=True)

            # --- Financial Savings Showcase ---
            saved_total = cost.get('money_saved_per_serving', 12.0) * rc.get('servings', 2)
            st.markdown(f"""
            <div class="savings-showcase">
                <div style='text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.8rem; font-weight: 700; color: #86efac;'>Wallet Intelligence Report</div>
                <h3>🎉 Total Estimated Savings: ${saved_total:.2f}</h3>
                <p style='color: #dcfce7; margin: 4px 0 12px 0;'>Cost to cook at home: <b>${cost.get('cost_to_cook_per_serving', 2.50):.2f}/serving</b> vs. Restaurant/Delivery: <b>${cost.get('takeout_equivalent_cost', 15.00):.2f}/serving</b></p>
                <div style='display: flex; gap: 15px; flex-wrap: wrap;'>
                    <span style='background: rgba(255,255,255,0.15); padding: 4px 12px; border-radius: 6px; font-size: 0.85rem;'>⚡ Protein Efficiency: <b>${cost.get('cost_per_gram_protein', 0.06):.2f} / gram</b></span>
                    <span style='background: rgba(255,255,255,0.15); padding: 4px 12px; border-radius: 6px; font-size: 0.85rem;'>🌱 Food Waste Prevented</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # --- Macronutrient Visuals ---
            macro_col1, macro_col2 = st.columns([1, 1])
            with macro_col1:
                st.markdown("#### 🏋️ Macronutrients (Per Serving)")
                nm1, nm2 = st.columns(2)
                nm1.metric("Calories", f"{nutr.get('calories', 500)} kcal")
                nm2.metric("Protein", f"{nutr.get('protein_g', 42)}g")
                nm3, nm4 = st.columns(2)
                nm3.metric("Carbs", f"{nutr.get('carbs_g', 45)}g")
                nm4.metric("Healthy Fats", f"{nutr.get('fat_g', 14)}g")
                
                if rc.get("macro_alignment_tip"):
                    st.info(f"💡 {rc.get('macro_alignment_tip')}")

            with macro_col2:
                pie = render_macro_donut(
                    nutr.get('protein_g', 42),
                    nutr.get('carbs_g', 45),
                    nutr.get('fat_g', 14),
                    "Serving Macro Distribution"
                )
                if pie:
                    st.plotly_chart(pie, use_container_width=True)

            # --- Ingredients & Cooking Steps ---
            st.markdown("---")
            ing_col1, ing_col2 = st.columns(2)
            with ing_col1:
                st.markdown("#### 🛒 Ingredients From Your Pantry")
                for ing in rc.get("ingredients_used", []):
                    st.markdown(f"• **{ing}**")

            with ing_col2:
                st.markdown("#### 🧂 Common Staples / Seasoning")
                for add in rc.get("additional_needed", []):
                    st.markdown(f"• {add}")

            st.markdown("#### 📋 Step-by-Step Instructions")
            for idx, step in enumerate(rc.get("instructions", []), 1):
                st.markdown(f"""
                <div class="step-box">
                    <b>Step {idx}:</b> {step}
                </div>
                """, unsafe_allow_html=True)

            if rc.get("zero_waste_tip"):
                st.success(f"🌱 **Zero-Waste Hack:** {rc.get('zero_waste_tip')}")

            # --- Log Meal Action ---
            st.markdown("---")
            if st.button("🏆 I Cooked This Meal! (Log to Today's Dashboard)", type="primary", use_container_width=True):
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
                st.toast("Meal successfully logged! Look at your updated dashboard metrics above.", icon="🎉")
                st.rerun()

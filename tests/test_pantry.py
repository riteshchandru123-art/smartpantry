import os
import pytest
from datetime import datetime, timedelta
import db
from ai_service import DetectedItem, VisionAnalysisResult, Recipe

TEST_DB = "test_pantry.db"

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    db.init_db(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_add_and_get_items():
    item_id = db.add_item("Spinach", "1 bunch", "Produce", "2026-10-20", "Organic", db_path=TEST_DB)
    assert item_id > 0

    items = db.get_all_items(db_path=TEST_DB)
    assert len(items) == 1
    assert items[0]["name"] == "Spinach"
    assert items[0]["quantity"] == "1 bunch"
    assert items[0]["category"] == "Produce"

def test_expiring_soon_items():
    today = datetime.now()
    expiring_soon = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    expiring_later = (today + timedelta(days=10)).strftime("%Y-%m-%d")

    db.add_item("Milk", "1L", "Dairy", expiring_soon, db_path=TEST_DB)
    db.add_item("Rice", "5kg", "Pantry", expiring_later, db_path=TEST_DB)

    urgent = db.get_expiring_soon_items(days_ahead=3, db_path=TEST_DB)
    assert len(urgent) == 1
    assert urgent[0]["name"] == "Milk"

def test_delete_item():
    id1 = db.add_item("Eggs", "6 pack", "Dairy", "2026-10-25", db_path=TEST_DB)
    assert len(db.get_all_items(db_path=TEST_DB)) == 1

    deleted = db.delete_item(id1, db_path=TEST_DB)
    assert deleted is True
    assert len(db.get_all_items(db_path=TEST_DB)) == 0

def test_pydantic_schemas():
    item = DetectedItem(name="Greek Yogurt", quantity="500g", category="Dairy", estimated_shelf_life_days=7)
    assert item.name == "Greek Yogurt"
    assert item.estimated_shelf_life_days == 7

    res = VisionAnalysisResult(items=[item])
    assert len(res.items) == 1

    rec = Recipe(
        title="Quick Veggie Scramble",
        prep_time_minutes=5,
        cook_time_minutes=10,
        servings=2,
        ingredients_used=["Spinach", "Eggs"],
        additional_needed=["Olive oil", "Salt"],
        instructions=["Chop spinach", "Whisk eggs", "Cook in pan"],
        zero_waste_tip="Uses wilting greens before they spoil."
    )
    assert rec.servings == 2

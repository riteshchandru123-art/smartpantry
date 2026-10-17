import os
import unittest
from datetime import datetime, timedelta
import db

TEST_DB = "test_nutriwallet.db"

class TestNutriWalletDB(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        db.init_db(TEST_DB)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_add_and_retrieve_with_macros_and_price(self):
        item_id = db.add_item(
            name="Chicken Breast",
            quantity="500g",
            category="Meat/Protein",
            expiry_date="2026-10-25",
            notes="Lean source",
            price=6.50,
            calories=600,
            protein_g=120.0,
            carbs_g=0.0,
            fat_g=8.0,
            db_path=TEST_DB
        )
        self.assertGreater(item_id, 0)

        items = db.get_all_items(db_path=TEST_DB)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "Chicken Breast")
        self.assertEqual(items[0]["price"], 6.50)
        self.assertEqual(items[0]["protein_g"], 120.0)

    def test_inventory_total_value(self):
        db.add_item("Eggs", "12 pack", "Dairy", price=3.50, db_path=TEST_DB)
        db.add_item("Oats", "1kg", "Pantry", price=4.20, db_path=TEST_DB)
        
        total = db.get_total_inventory_value(db_path=TEST_DB)
        self.assertEqual(total, 7.70)

    def test_meal_logging_and_today_summary(self):
        db.log_meal(
            recipe_title="High Protein Chicken Bowl",
            calories=550,
            protein_g=52.0,
            carbs_g=40.0,
            fat_g=12.0,
            cost=3.20,
            takeout_savings=13.80,
            db_path=TEST_DB
        )

        summary = db.get_today_nutrition_summary(db_path=TEST_DB)
        self.assertEqual(summary["meals_count"], 1)
        self.assertEqual(summary["calories"], 550)
        self.assertEqual(summary["protein_g"], 52.0)
        self.assertEqual(summary["savings"], 13.80)

if __name__ == "__main__":
    unittest.main()

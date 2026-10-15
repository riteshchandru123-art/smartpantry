import os
import unittest
from datetime import datetime, timedelta
import db

TEST_DB = "test_unittest_pantry.db"

class TestPantryDB(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        db.init_db(TEST_DB)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_add_and_retrieve_items(self):
        item_id = db.add_item("Spinach", "1 bunch", "Produce", "2026-10-20", "Organic", db_path=TEST_DB)
        self.assertGreater(item_id, 0)

        items = db.get_all_items(db_path=TEST_DB)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "Spinach")
        self.assertEqual(items[0]["quantity"], "1 bunch")
        self.assertEqual(items[0]["category"], "Produce")

    def test_expiring_soon_filter(self):
        today = datetime.now()
        exp_soon = (today + timedelta(days=2)).strftime("%Y-%m-%d")
        exp_later = (today + timedelta(days=10)).strftime("%Y-%m-%d")

        db.add_item("Fresh Milk", "1L", "Dairy", exp_soon, db_path=TEST_DB)
        db.add_item("Dry Lentils", "2kg", "Pantry", exp_later, db_path=TEST_DB)

        urgent = db.get_expiring_soon_items(days_ahead=3, db_path=TEST_DB)
        self.assertEqual(len(urgent), 1)
        self.assertEqual(urgent[0]["name"], "Fresh Milk")

    def test_delete_item(self):
        id1 = db.add_item("Eggs", "6 pack", "Dairy", "2026-10-25", db_path=TEST_DB)
        self.assertEqual(len(db.get_all_items(db_path=TEST_DB)), 1)

        result = db.delete_item(id1, db_path=TEST_DB)
        self.assertTrue(result)
        self.assertEqual(len(db.get_all_items(db_path=TEST_DB)), 0)

if __name__ == "__main__":
    unittest.main()

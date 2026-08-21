"""Tests for Ramp expense deductibility demo."""

import unittest
from oa_client import OAClient
import deductibility_check
import ramp_client


class RampExpenseDemoTests(unittest.TestCase):
    def setUp(self):
        self.oa = OAClient(token=None)
        self.gb_skill = self.oa.get_skill("gb-expense-deductibility")
        self.us_skill = self.oa.get_skill("us-expense-deductibility")

    def test_mock_oa_client(self):
        self.assertEqual(self.gb_skill["tier"], 1)
        self.assertIn("James Power", self.gb_skill["verifier"])
        self.assertEqual(self.us_skill["tier"], 1)
        self.assertIn("Amir Pelinkovic", self.us_skill["verifier"])

    def test_gb_client_entertainment_not_deductible(self):
        tx = {
            "jurisdiction": "GB",
            "ramp_category": "Meals & Entertainment",
            "memo": "Dinner with client ACME Ltd",
            "merchant": "The Ledbury",
            "amount": 240.0,
            "currency": "GBP",
        }
        res = deductibility_check.check(tx, self.gb_skill)
        self.assertEqual(res["status"], "warn")
        self.assertIn("NOT deductible", res["headline"])

    def test_us_meals_50_percent(self):
        tx = {
            "jurisdiction": "US",
            "ramp_category": "Meals",
            "memo": "Lunch with prospect re: Q3 deal",
            "merchant": "Joe's Grill",
            "amount": 120.0,
            "currency": "USD",
        }
        res = deductibility_check.check(tx, self.us_skill)
        self.assertEqual(res["status"], "info")
        self.assertIn("50% deductible", res["headline"])

    def test_us_entertainment_not_deductible(self):
        tx = {
            "jurisdiction": "US",
            "ramp_category": "Entertainment",
            "memo": "NBA tickets with client",
            "merchant": "Ticketmaster",
            "amount": 600.0,
            "currency": "USD",
        }
        res = deductibility_check.check(tx, self.us_skill)
        self.assertEqual(res["status"], "warn")
        self.assertIn("NOT deductible", res["headline"])

    def test_samples_extraction(self):
        txns = ramp_client.extract("samples/transactions.json")
        self.assertEqual(len(txns), 5)
        norm = ramp_client.normalize(txns[0])
        self.assertEqual(norm["merchant"], "The Ledbury")
        self.assertEqual(norm["jurisdiction"], "GB")


if __name__ == "__main__":
    unittest.main()

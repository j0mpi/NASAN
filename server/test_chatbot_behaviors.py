import os
import sys
import unittest

os.environ["USE_LLM"] = "false"
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from entity_extractor import extract


class ChatbotBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def chat(self, message):
        return self.client.post("/api/chat", json={"message": message}).get_json()

    def test_family_of_alumni_is_not_name_lookup(self):
        response = self.chat("My dad is a graduate of NU")

        self.assertEqual(response["intent"], "ask_eligibility")
        self.assertEqual(response["entities"]["affiliation"], "family of alumni")
        self.assertEqual(response["results"][0]["Scholarship Name"], "Family of Alumni")

    def test_sibling_affiliation_returns_sibling_discount(self):
        response = self.chat("My sibling is currently enrolled at NU")

        self.assertEqual(response["intent"], "ask_eligibility")
        self.assertEqual(response["entities"]["affiliation"], "sibling of current student")
        self.assertEqual(response["results"][0]["Scholarship Name"], "Sibling Discount")

    def test_deadline_without_name(self):
        response = self.chat("Until what date can I send in my application")

        self.assertEqual(response["intent"], "ask_deadline")
        self.assertIn("before November 3", response["reply"])
        self.assertEqual(response["results"], [])

    def test_typo_tolerant_incoming_freshman(self):
        response = self.chat("i am an incomng freshman with gwa 96")

        self.assertEqual(response["intent"], "ask_eligibility")
        self.assertEqual(response["entities"]["student_type"], "incoming first-year")
        self.assertEqual(response["entities"]["gwa"], 96)
        self.assertTrue(response["results"])
        self.assertTrue(all("%" in result["Minimum GWA"] for result in response["results"]))

    def test_existing_cases_keep_their_intents(self):
        expected_intents = {
            "Hi": "greet",
            "I'm an incoming first year student with a GWA of 98": "ask_eligibility",
            "My mom is a police officer": "ask_details",
            "I'm a continuing student with a 3.5 CGWA": "ask_eligibility",
        }

        for message, expected in expected_intents.items():
            with self.subTest(message=message):
                self.assertEqual(extract(message)["intent"], expected)


if __name__ == "__main__":
    unittest.main()

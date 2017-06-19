import unittest
from . import api


class TestExist(unittest.TestCase):
    def setUp(self):
        self.test = api.Exist()

    def test_instantiation_with_token(self):
        #TODO
        test2 = api.Exist("token")
        self.assertEqual(test2.token,
                         "token")

    def test_instantiation_username_or_password(self):
        self.assertRaises(ValueError, api.Exist, username="Awesomecase")

    def test_instantiation_kwargs_bad_kwarg(self):
        self.assertRaises(ValueError, api.Exist, badkey="llama")

    def test_instantiation_set_attributes_dict(self):
        attributes = {"all_attributes": [], "steps": [],
                      "steps_active_min": [], "steps_distance": [],
                      "steps_goal": [], "productive_min": [],
                      "distracting_min": [], "neutral_min": [],
                      "productive_min_goal": [], "commits": [],
                      "tasks_completed": [], "mood": [], "mood_note": [],
                      "sleep": [], "time_in_bed": [], "sleep_start": [],
                      "sleep_end": [], "sleep_awakenings": [],
                      "sleep_goal": [], "events": [],
                      "events_duration": [], "weight": [],
                      "heartrate": [], "tracks": [], "location": [],
                      "checkins": [], "tweets": [],
                      "twitter_mentions": [], "location_name": []}

        for key in attributes:
            with self.subTest(key=key):
                self.assertIn(key, self.test.attributes)

    def test_get_token_username_or_password_but_not_both(self):
        #TODO
        self.assertRaises(TypeError, self.test.get_token, "username")

    def test_get_token_bad_username_or_password(self):
        self.assertRaises(api.requests.HTTPError, self.test.get_token,
                          "username", "password")

    def test_get_token_works(self):
        self.test.get_token("user", "pass")
        self.assertEqual(self.test.token,
                         "token")

    def test_get_attributes_kwargs_limit(self):
        amounts = [0, -1, 32]
        for amount in amounts:
            with self.subTest(amount=amount):
                self.assertRaises(KeyError, self.test.get_attributes,
                                  limit=amount)

    #def test_get_attributes_kwargs_date_min(self):
    #    self.test.get_attributes, date_min="2017-06-06", limit=31

    def test_get_attributes_limit(self):
        self.test.get_attributes(limit=2)
        assert len(self.test.attributes["all_attributes"][-1].values[0]["values"]) == 2

    def test_get_attributes_kwargs_date_max(self):
        self.test.get_attributes(date_max="2017-06-06")
        assert self.test.attributes["all_attributes"][-1].values[0]["values"][0]["date"] == "2017-06-06"

    def test_get_attributes_raises_if_no_token(self):
        self.test.token = ""
        self.assertRaises(ValueError, self.test.get_attributes)

    def test_get_attributes_raises_if_bad_kwarg(self):
        self.assertRaises(KeyError, self.test.get_attributes,
                          dae_min="2017-06-05")

    def test_get_attributes_raises_if_bad_requests(self):
        self.assertRaises(api.requests.HTTPError, self.test.get_attributes,
                          date_max="1000000000")

if __name__ == "__main__":
    unittest.main()

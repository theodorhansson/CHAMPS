import unittest
import main


class PhotonicTest(unittest.TestCase):
    def test_dict_2_lower(self):
        test_dict = {
            "ABC": "EFG",
            "HI": {"JK": "HK"},
            "volTage": 10,
            "A": {"B": {"C": {"D": 7}}},
            "78": 12,
            "12A": "abc",
        }

        correct_dict = {
            "abc": "efg",
            "hi": {"jk": "hk"},
            "voltage": 10,
            "a": {"b": {"c": {"d": 7}}},
            "78": 12,
            "12a": "abc",
        }

        lower_dict = main.dict_2_lower(test_dict)
        self.assertEqual(lower_dict, correct_dict)


if __name__ == "__main__":
    unittest.main()

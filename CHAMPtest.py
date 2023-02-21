import unittest
import main
import utils


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

    def test_signed_bits2int(self):
        test_cases = [
            ("11", -1),
            ("10001", -15),
            ("100001", -31),
            (str(bin(0xE9A2))[2:], -5726),
            ("00011", 3),
        ]

        for case in test_cases:
            test_value = case[0]
            test_reference = case[1]
            answer = utils.signed_bits2int(test_value)
            self.assertEqual(test_reference, answer, msg=f"{test_reference}")


if __name__ == "__main__":
    unittest.main()

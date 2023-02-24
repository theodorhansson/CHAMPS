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

        lower_dict = utils.dict_2_lower(test_dict)
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

    def test_argument_checker(self):
        required = ["value1", "value2"]
        optional = {
            "value3": 0,
            "value4": 1,
        }

        # Missing required argument and optional
        # Expected: Exception
        config = {"value1": 2, "value3": 4}
        with self.assertRaises(Exception):
            utils.argument_checker(config, required, optional)

        # Missing required argument
        # Expected: Exception
        config = {"value1": 2, "value3": 4, "value4": 69}
        with self.assertRaises(Exception):
            utils.argument_checker(config, required, optional)

        # Too many arguments
        # Expected: Warning
        config = {"value1": 2, "value2": 4, "value5": 3}
        with self.assertWarns(UserWarning):
            utils.argument_checker(config, required, optional)

        # All arguments included
        # Expected: Nothing
        config = {"value1": 2, "value2": 4, "value3": 4, "value4": 69}
        utils.argument_checker(config, required, optional)

        # All but optional included
        # Expected: Nothing
        config = {"value1": 2, "value2": 4}
        utils.argument_checker(config, required, optional)

    def _test_optional_arguments_merge(self):  # TODO: finish me
        conf = {"type": "chalmers", "abc": "123", "petg": 111}
        opt = {"petg": 222, "PPP": "ASDASD"}

        config = {
            "value1": 1,
            "value2": 1,
        }

        print(optional_arguments_merge(conf, opt))


if __name__ == "__main__":
    unittest.main()

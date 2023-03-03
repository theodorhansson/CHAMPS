import unittest
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

        print(utils.optional_arguments_merge(conf, opt))

    def test_closest_matcher(self):
        accepted = [0, 1, 2, 3, 4]

        # query, reference
        queries_no_arg = (
            (1, 1),
            (1.5, 2),
            (0.5, 1),
            (-100, 0),
            (100, 4),
        )

        for query, reference in queries_no_arg:
            answer = utils.closest_matcher(query, accepted)
            self.assertEqual(reference, answer)

        # query, reference, round_type
        queries_args = (
            (1, 1, "down"),
            (1, 1, "up"),
            (1.5, 1, "down"),
            (1.5, 2, "up"),
            (-100, 0, "up"),
            (100, 4, "up"),
            (-100, 0, "down"),
            (100, 4, "down"),
            (0.1, 0, "regularly"),
            (0.9, 1, "regularly"),
            (-100, 0, "regularly"),
            (100, 4, "regularly"),
        )

        for query, reference, r_type in queries_args:
            answer = utils.closest_matcher(query, accepted, round_type=r_type)
            self.assertEqual(reference, answer, msg=(reference, answer))

        # query, reference, round_type, exception trigger
        queries_args_exception = (
            (1, 1, "exact", False),
            (1.5, None, "exact", True),
            (-100, None, "exact", True),
            (100, None, "exact", True),
        )

        for query, reference, r_type, trigger in queries_args_exception:
            if trigger:
                with self.assertRaises(Exception):
                    utils.closest_matcher(query, accepted, round_type=r_type)
            else:
                utils.closest_matcher(query, accepted, round_type=r_type)

    def test_interval_2_points(self):
        # specification, points/result
        case_list = (
            ([[0, 1, 10]], [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]),
            ([0, 1, 10], [[0], [1], [10]]),
            (
                [0, 1, 10, [0, 1, 10]],
                [[0], [1], [10], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],
            ),
            (
                [[0, 0.9, 10]],
                [[0, 0.9, 1.8, 2.7, 3.6, 4.5, 5.4, 6.3, 7.2, 8.1, 9, 9.9, 10]],
            ),
            (
                [[0, 0.9, 10], 69],
                [[0, 0.9, 1.8, 2.7, 3.6, 4.5, 5.4, 6.3, 7.2, 8.1, 9, 9.9, 10], [69]],
            ),
            (
                [69, [0, 0.9, 10]],
                [[69], [0, 0.9, 1.8, 2.7, 3.6, 4.5, 5.4, 6.3, 7.2, 8.1, 9, 9.9, 10]],
            ),
            (1, [[1]]),
            ([[0, 1, "10"]], [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]),
            ([0, 1, "10"], [[0], [1], [10]]),
        )

        for case in case_list:
            query = case[0]
            reference = case[1]
            answer = list(utils.interval_2_points(query))

            self.assertEqual(answer, reference, msg=f"{case=}")

        case_list_exception = (
            None,
            [[1]],
            [[1, 2]],
            [[1, 2, 3, 4]],
            [],
            [[1, 2, "sup bro"]],
        )

        for exc_case in case_list_exception:
            with self.assertRaises(TypeError):
                self.test_interval_2_points(exc_case)

    def test_number_recaster(self):
        cases = (
            (1, 1),
            ("1", 1),
            ([1, "2"], [1, 2]),
            ((1, "2"), (1, 2)),
        )

        for case in cases:
            query = case[0]
            reference = case[1]
            answer = utils.list_number_recaster(query)
            self.assertEqual(reference, answer)


if __name__ == "__main__":
    unittest.main()

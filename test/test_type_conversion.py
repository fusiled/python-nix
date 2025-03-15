import sys
import unittest
from nix.expr import State, Type
from nix.store import Store


class PythonToNixConversion(unittest.TestCase):
    def alloc_value(self):
        st = Store()
        state = State([], st)
        return state.alloc_val()

    def generic_type_test(self, pyval, expected_nix_type: Type, conv_function):
        val = self.alloc_value()
        val.set(pyval)
        self.assertEqual(val.get_type(), expected_nix_type)
        self.assertEqual(conv_function(val), pyval)

    def generic_type_test_array(self, testcases, expected_nix_type: Type, conv_function):
        for pyval, assertion in testcases:
            if assertion is None:
                self.generic_type_test(pyval, expected_nix_type, conv_function)
                continue
            with self.assertRaises(assertion):
                self.generic_type_test(pyval, expected_nix_type, conv_function)

    def test_integer(self):
        all_tests = [
            (None, AssertionError),
            (0, None),
            (-1, None),
            ((1 << 32) - 1, None),
            ((1 << 32), None),
            (-(1 << 32), None),
            ((1 << 63)-1, None),
            (1 << 63, OverflowError),
            (1 << 64, OverflowError),
            (-((1 << 63)+1), OverflowError)
        ]
        self.generic_type_test_array(all_tests, Type.int, int)

    def test_string(self):
        all_tests = [
            (None, AssertionError),
            ("Hello Dummy", None),
            ("", None),
        ]
        self.generic_type_test_array(all_tests, Type.string, str)

    def test_bool(self):
        all_tests = [
            (None, AssertionError),
            (True, None),
            (False, None),
        ]
        self.generic_type_test_array(all_tests, Type.bool, bool)

    def test_float(self):
        all_tests = [
            (None, AssertionError),
            (0.0, None),
            (-0.0, None),
            (sys.float_info.max, None),
            (sys.float_info.min, None),
        ]
        self.generic_type_test_array(all_tests, Type.float, float)

    def test_null(self):
        self.generic_type_test(None, Type.null, lambda v: v._to_python())


if __name__ == "__main__":
    unittest.main()

"""
Basic tests for the utility functions.
"""
import sys
import os
import unittest

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils import format_response, validate_input


class TestUtilityFunctions(unittest.TestCase):
    def test_format_response(self):
        """Test the format_response function"""
        data = {"name": "Test"}
        result = format_response(data, message="Test message")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Test message")
        self.assertEqual(result["data"], data)
    
    def test_validate_input(self):
        """Test the validate_input function"""
        data = {"name": "Test", "age": 25}
        
        # Test with all fields present
        is_valid, missing = validate_input(data, ["name", "age"])
        self.assertTrue(is_valid)
        self.assertEqual(len(missing), 0)
        
        # Test with missing fields
        is_valid, missing = validate_input(data, ["name", "age", "email"])
        self.assertFalse(is_valid)
        self.assertEqual(missing, ["email"])


if __name__ == "__main__":
    unittest.main()

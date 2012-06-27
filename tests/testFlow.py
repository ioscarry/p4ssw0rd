import pass_check
import unittest

class testFlow(unittest.TestCase):
    def setUp(self):
        pass

    def testDictionary(self):
        """Test that dictionary words are found first"""
        password = "thing"
        pass_check.checkPassword(password)

    def tearDown(self):
        pass
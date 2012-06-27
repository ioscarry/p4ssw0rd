import unittest
import pass_check


class TestChecks(unittest.TestCase):
    def testFindDate(self):
        pw = pass_check.Password("2008-03-30")
        self.assertEqual(pw.findDate(), True)
        self.assertEqual(pw.parts)

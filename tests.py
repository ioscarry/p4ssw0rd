import unittest
from tests.testChecks import TestFind, TestRemove, TestOther, TestCombined

if __name__ == "__main__":
    suite = [
        unittest.makeSuite(TestFind),
        unittest.makeSuite(TestRemove),
        unittest.makeSuite(TestOther),
        unittest.makeSuite(TestCombined)]
    alltests = unittest.TestSuite(suite)

    runner = unittest.TextTestRunner()
    runner.run(alltests)
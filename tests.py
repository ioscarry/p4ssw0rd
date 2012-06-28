import unittest
from tests.testChecks import TestChecks

if __name__ == "__main__":
    suite = [
        unittest.makeSuite(TestChecks)]
    alltests = unittest.TestSuite(suite)

    runner = unittest.TextTestRunner()
    runner.run(alltests)
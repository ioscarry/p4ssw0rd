import unittest
import pass_check

class TestChecks(unittest.TestCase):
    def testFindDate(self):
        pw = pass_check.Password("2008-03-30")
        self.assertEqual(pw.findDate(), True)
        #self.assertEqual(pw.parts)

    def testFindWord(self):
        pw = pass_check.Password("illinois")
        self.assertEqual(pw.findWord(), True)
        self.assertEqual(pw.parts[0].word, "illinois")
        self.assertEqual(pw.parts[0].type, "word")
        self.assertEqual(pw.parts[0].mutations, [])

    def testFindWordLeet(self):
        pw = pass_check.Password("t3rr!fy")
        self.assertEqual(pw.findWord(), True)
        self.assertEqual(pw.parts[0].word, "terrify")
        self.assertEqual(pw.parts[0].type, "word")
        self.assertEqual(pw.parts[0].mutations[0].type, "leet")
        self.assertEqual(pw.parts[0].mutations[0].index, [1, 4])

    def testFindWordCap(self):
        pw = pass_check.Password("rOBert")
        self.assertEqual(pw.findWord(), True)
        self.assertEqual(pw.parts[0].word, "robert")
        self.assertEqual(pw.parts[0].type, "word")
        self.assertEqual(pw.parts[0].mutations[0].type, "case")
        self.assertEqual(pw.parts[0].mutations[0].index, [1, 2])

    def testFindWordCapLeet(self):
        pw = pass_check.Password("T3l3gr4PH")
        self.assertEqual(pw.findWord(), True)
        self.assertEqual(pw.parts[0].word, "telegraph")
        self.assertEqual(pw.parts[0].type, "word")
        self.assertEqual(pw.parts[0].mutations[0].type, "case")
        self.assertEqual(pw.parts[0].mutations[0].index, [0, 7, 8])
        self.assertEqual(pw.parts[0].mutations[1].type, "leet")
        self.assertEqual(pw.parts[0].mutations[1].index, [1, 3, 6])

    def testFindDateYMD(self):
        pw = pass_check.Password("2009/04/21")
        self.assertEqual(pw.findDate(), True)
        self.assertEqual(pw.parts[0].word, "2009/04/21")
        self.assertEqual(pw.parts[0].type, "date-common-YMD")
        self.assertEqual(pw.parts[0].mutations, [])

    def testFindDateYM(self):
        pw = pass_check.Password("200809")
        self.assertEqual(pw.findDate(), True)
        self.assertEqual(pw.parts[0].word, "200809")
        self.assertEqual(pw.parts[0].type, "date-common-YM")
        self.assertEqual(pw.parts[0].mutations, [])

    def testFindDateMD(self):
        pw = pass_check.Password("01.20")
        self.assertEqual(pw.findDate(), True)
        self.assertEqual(pw.parts[0].word, "01.20")
        self.assertEqual(pw.parts[0].type, "date-common-MD")
        self.assertEqual(pw.parts[0].mutations, [])

    def testFindDateY(self):
        pw = pass_check.Password("1949")
        self.assertEqual(pw.findDate(), True)
        self.assertEqual(pw.parts[0].word, "1949")
        self.assertEqual(pw.parts[0].type, "date-common-Y")
        self.assertEqual(pw.parts[0].mutations, [])

if __name__ == "__main__":
    unittest.main()
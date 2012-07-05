import unittest
import pass_check

class TestFind(unittest.TestCase):
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

    def testFindDatePart(self):
        pw = pass_check.Password("102399842")
        self.assertEqual(pw.findDate(), True)
        self.assertEqual(pw.parts[0].word, "102399")
        self.assertEqual(pw.parts[0].type, "date")
        self.assertEqual(pw.parts[0].mutations, [])

    def testFindDateYMD(self):
        pw = pass_check.Password("2009/04/21")
        self.assertEqual(pw.findDate(), True)
        self.assertEqual(pw.parts[0].word, "2009/04/21")
        self.assertEqual(pw.parts[0].type, "date")
        self.assertEqual(pw.parts[0].mutations, [])

    def testFindDateYM(self):
        pw = pass_check.Password("200809")
        self.assertEqual(pw.findDate(), True)
        self.assertEqual(pw.parts[0].word, "200809")
        self.assertEqual(pw.parts[0].type, "date")
        self.assertEqual(pw.parts[0].mutations, [])

    def testFindDateMD(self):
        pw = pass_check.Password("01.20")
        self.assertEqual(pw.findDate(), True)
        self.assertEqual(pw.parts[0].word, "01.20")
        self.assertEqual(pw.parts[0].type, "date")
        self.assertEqual(pw.parts[0].mutations, [])

    def testFindDateY(self):
        pw = pass_check.Password("1949")
        self.assertEqual(pw.findDate(), True)
        self.assertEqual(pw.parts[0].word, "1949")
        self.assertEqual(pw.parts[0].type, "date")
        self.assertEqual(pw.parts[0].mutations, [])

    def testFindDateFail(self):
        pw = pass_check.Password("9235590291")
        self.assertEqual(pw.findDate(), False)

    def testFindBorderSimple(self):
        pw = pass_check.Password("!!,,,,,,,,!!")
        pass_check.findParts(pw)
        self.assertEqual(pw.parts[0].word, "!!")
        self.assertEqual(pw.parts[0].type, "repetition")
        self.assertEqual(pw.parts[0].mutations, [])
        self.assertEqual(pw.parts[1].word, ",,,,,,,,")
        self.assertEqual(pw.parts[1].type, "repetition")
        self.assertEqual(pw.parts[1].mutations, [])
        self.assertEqual(pw.parts[2].word, "!!")
        self.assertEqual(pw.parts[2].type, "repetition")
        self.assertEqual(pw.parts[2].mutations, [])

    def testBinarySearch(self):
        # First entry in 9.dic
        pw = pass_check.Password("'prentice")
        self.assertEqual(pw.findWord(), True)
        self.assertEqual(pw.parts[0].word, "'prentice")
        self.assertEqual(pw.parts[0].type, "word")
        self.assertEqual(pw.parts[0].mutations, [])
        # Last entry in 7.dic
        pw = pass_check.Password("zzzzzzy")
        self.assertEqual(pw.findWord(), True)
        self.assertEqual(pw.parts[0].word, "zzzzzzy")
        self.assertEqual(pw.parts[0].type, "word")
        self.assertEqual(pw.parts[0].mutations, [])
        # Middle entry in 14.dic
        pw = pass_check.Password("longways dance")
        self.assertEqual(pw.findWord(), True)
        self.assertEqual(pw.parts[0].word, "longways dance")
        self.assertEqual(pw.parts[0].type, "word")
        self.assertEqual(pw.parts[0].mutations, [])

class TestRemove(unittest.TestCase):
    def testRemoveCase(self):
        pw = pass_check.Password("aAaAaaAAaAA")
        self.assertEqual(pw.removeCase(
            pw.parts[0].word), ([1, 3, 6, 7, 9, 10], "aaaaaaaaaaa"))

        pw = pass_check.Password("34a90ReElo@A")
        self.assertEqual(pw.removeCase(
            pw.parts[0].word), ([5, 7, 11], "34a90reelo@a"))

    def testRemoveLeet(self):
        pw = pass_check.Password("0mg")
        for i in pw.removeLeet(pw.parts[0].word):
            self.assertEqual(i, ([0], "omg"))
        pw = pass_check.Password("!ll!n0i5")
        for i in pw.removeLeet(pw.parts[0].word):
            self.assertEqual(i, ([0,3,5,7], "illinois"))
        pw = pass_check.Password("0mg")

    def testRemoveDelimiter(self):
        pw = pass_check.Password("p-a-s-s-w-o-r-d")
        self.assertEqual(pw.removeDelimiter(
            pw.parts[0].word), ([1,3,5,7,9,11,13], "password"))
        pw = pass_check.Password("-l-i-s-a-")
        self.assertEqual(pw.removeDelimiter(
            pw.parts[0].word), ([0,2,4,6,8], "lisa"))
        pw = pass_check.Password(".n.o.t.g.o.o.d2008")
        self.assertEqual(pw.removeDelimiter(
            pw.parts[0].word), ([0,2,4,6,8,10,12], "notgood2008"))
        pw = pass_check.Password(" h i m o m")
        self.assertEqual(pw.removeDelimiter(
            pw.parts[0].word), ([0,2,4,6,8], "himom"))
        pw = pass_check.Password("f_a_il")
        self.assertEqual(pw.removeDelimiter(
            pw.parts[0].word), ([], "f_a_il"))

    def testBruteForce(self):
        pw = pass_check.Password("owirudyas")
        pw.findBruteForce(0)
        self.assertEqual(pw.parts[0].word, "owirudyas")
        self.assertEqual(pw.parts[0].type, "bruteforce")
        self.assertEqual(pw.parts[0].cost, 26 ** 9)

        pw = pass_check.Password("94532")
        pw.findBruteForce(0)
        self.assertEqual(pw.parts[0].word, "94532")
        self.assertEqual(pw.parts[0].type, "bruteforce")
        self.assertEqual(pw.parts[0].cost, 10 ** 5)

        pw = pass_check.Password("94$532")
        pw.findBruteForce(0)
        self.assertEqual(pw.parts[0].word, "94$532")
        self.assertEqual(pw.parts[0].type, "bruteforce")
        self.assertEqual(pw.parts[0].cost, 72 ** 6)

        pw = pass_check.Password("CEPQOSWA")
        pw.findBruteForce(0)
        self.assertEqual(pw.parts[0].word, "CEPQOSWA")
        self.assertEqual(pw.parts[0].type, "bruteforce")
        self.assertEqual(pw.parts[0].cost, 26 ** 8)


class TestOther(unittest.TestCase):
    def testSubPermutations(self):
        pw = pass_check.Password("qwerty")
        expected = [
            ("", "", "qwerty"),
            ("", "y", "qwert"),
            ("q", "", "werty"),
            ("", "ty", "qwer"),
            ("q", "y", "wert"),
            ("qw", "", "erty"),
            ("", "rty", "qwe"),
            ("q", "ty", "wer"),
            ("qw", "y", "ert"),
            ("qwe", "", "rty")
        ]
        for index, (prefix, suffix, sub) in enumerate(pw.subPermutations(
            pw.parts[0].word, minLength=3)):
            self.assertEqual(expected[index], (prefix, suffix, sub))

        pw = pass_check.Password("seven")
        expected = [
            ("", "", "seven"),
            ("", "n", "seve"),
            ("s", "", "even")
        ]
        for index, (prefix, suffix, sub) in enumerate(pw.subPermutations(
            pw.parts[0].word, minLength=4)):
            self.assertEqual(expected[index], (prefix, suffix, sub))

class TestCombined(unittest.TestCase):
    """Documentation for ideal cases. These may fail until problems are
    solved, or wordlists are finalized."""
    def testBorderConflict(self):
        """Tests that conflicts between borders and leet replacements are
        handled properly. Should read $$money$$ instead of $$moneys$."""
        pw = pass_check.Password("$$money$$")
        pass_check.findParts(pw)
        self.assertEqual(pw.parts[0].word, "$$")
        self.assertEqual(pw.parts[0].type, 'repetition')
        self.assertEqual(pw.parts[0].mutations, [])
        self.assertEqual(pw.parts[1].word, "money")
        self.assertEqual(pw.parts[1].type, 'word')
        self.assertEqual(pw.parts[1].mutations, [])
        self.assertEqual(pw.parts[2].word, "$$")
        self.assertEqual(pw.parts[2].type, 'repetition')
        self.assertEqual(pw.parts[2].mutations, [])

    def testMultipleBorders(self):
        """Tests two borders with an identical delimiter (should be picked up as
        a single border with delimiter between two dictionary words)"""
        pw = pass_check.Password("!!tim!!tammy!!")
        pass_check.findParts(pw)
        self.assertEqual(pw.parts[0].word, "!!")
        self.assertEqual(pw.parts[0].type, 'repetition')
        self.assertEqual(pw.parts[0].mutations, [])
        self.assertEqual(pw.parts[1].word, "tim")
        self.assertEqual(pw.parts[1].type, 'word')
        self.assertEqual(pw.parts[1].mutations, [])
        self.assertEqual(pw.parts[2].word, "!!")
        self.assertEqual(pw.parts[2].type, 'delimiter')
        self.assertEqual(pw.parts[2].mutations, [])
        self.assertEqual(pw.parts[3].word, "tammy")
        self.assertEqual(pw.parts[3].type, 'word')
        self.assertEqual(pw.parts[3].mutations, [])
        self.assertEqual(pw.parts[4].word, "!!")
        self.assertEqual(pw.parts[4].type, 'repetition')
        self.assertEqual(pw.parts[4].mutations, [])

if __name__ == "__main__":
    unittest.main()
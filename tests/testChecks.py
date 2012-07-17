import unittest
import pass_check

class TestMain(unittest.TestCase):
    def testAnalysis(self):
        """Test that main() runs and returns the correct analysis object."""
        result = pass_check.main("0000000000")
        self.assertEqual(result.word, "0000000000")
        self.assertGreater(result.cost, 1)
        self.assertEqual(result.parts[0].word, "0000000000")
        self.assertEqual(result.parts[0].type, "repetition")
        self.assertGreater(result.time, 0)

    def testRandomPassword(self):
        """Test that main() runs and returns a valid analysis object."""
        result = pass_check.main(randomPassword=True)
        self.assertTrue(bool(result.word))
        self.assertGreater(result.cost, 1)
        self.assertTrue(bool(result.parts[0].word))
        self.assertTrue(bool(result.parts[0].type))
        self.assertTrue(bool(result.word))

    def testTime(self):
        """Test random passwords, fail if any time is greater than 1"""
        for i in range(0, 20):
            result = pass_check.main(randomPassword=True)
            self.assertLess(result.time, 1)

    def testPatternWordRepeat(self):
        """Test that repeated words are identified."""
        result = pass_check.main("timertimer")
        self.assertGreater(result.cost, 1)
        self.assertEqual(result.parts[0].word, "timer")
        self.assertEqual(result.parts[0].pattern, "word-repeat")
        self.assertEqual(result.parts[1].word, "timer")
        self.assertEqual(result.parts[1].pattern, "word-repeat")

    def testPatternWordCombination(self):
        """Test that combinations of words are identified."""
        result = pass_check.main("wordthreat")
        self.assertGreater(result.cost, 1)
        self.assertEqual(result.parts[0].word, "word")
        self.assertEqual(result.parts[0].pattern, "word-combination")
        self.assertEqual(result.parts[1].word, "threat")
        self.assertEqual(result.parts[1].pattern, "word-combination")


    def testPatternWordCombinationDelimiter(self):
        """Test that two words with a single delimiter are identified."""
        result = pass_check.main("money$dollars")
        self.assertGreater(result.cost, 1)
        self.assertEqual(result.parts[0].word, "money")
        self.assertEqual(result.parts[0].pattern, "word-combination")
        self.assertEqual(result.parts[1].word, "$")
        self.assertEqual(result.parts[1].pattern, "word-combination-delimiter")
        self.assertEqual(result.parts[2].word, "dollars")
        self.assertEqual(result.parts[2].pattern, "word-combination")

    def testPatternBorderRepeat(self):
        """Test that a repeated border is identified: !!example!!"""
        result = pass_check.main("!!borders!!")
        self.assertGreater(result.cost, 1)
        self.assertEqual(result.parts[0].word, "!!")
        self.assertEqual(result.parts[0].pattern, "border-repeat")
        self.assertEqual(result.parts[1].word, "borders")
        self.assertEqual(result.parts[1].pattern, None)
        self.assertEqual(result.parts[2].word, "!!")
        self.assertEqual(result.parts[2].pattern, "border-repeat")

    def testPatternBorderMirror(self):
        """Test that a mirrored border is identified: ((example))"""
        result = pass_check.main("((mirrors))")
        self.assertGreater(result.cost, 1)
        self.assertEqual(result.parts[0].word, "((")
        self.assertEqual(result.parts[0].pattern, "border-mirror")
        self.assertEqual(result.parts[1].word, "mirrors")
        self.assertEqual(result.parts[1].pattern, None)
        self.assertEqual(result.parts[2].word, "))")
        self.assertEqual(result.parts[2].pattern, "border-mirror")

class TestFind(unittest.TestCase):
    def getNext(self, method, password):
        """Returns the first password part found when using the specified method
        for the object Password(password)."""
        pw = pass_check.Password(password)
        method = getattr(pw, method)
        method(pw.root.next[0])
        pw.addParts()
        return pw.root.next[0]

    def testFindWord(self):
        node = self.getNext("findWord", "illinois")
        self.assertEqual(node.word, "illinois")
        self.assertEqual(node.type, "word")
        self.assertEqual(node.mutations, [])

    def testFindWordFail(self):
        node = self.getNext("findWord", "102984582")
        self.assertNotEqual(node.type, "word")
        node = self.getNext("findWord", "aaaapppppeeee")
        self.assertNotEqual(node.type, "word")
        node = self.getNext("findWord", "dfgqwejklzxc")
        self.assertNotEqual(node.type, "word")

    def testFindWordLeetMulti(self):
        node = self.getNext("findWord", "t3rr!fy")
        self.assertEqual(node.word, "terrify")
        self.assertEqual(node.type, "word")
        self.assertEqual(node.mutations[0].type, "leetMulti")
        self.assertEqual(node.mutations[0].index, [1, 4])

    def testFindWordLeetOne(self):
        node = self.getNext("findWord", "appl3")
        self.assertEqual(node.word, "apple")
        self.assertEqual(node.type, "word")
        self.assertEqual(node.mutations[0].type, "leetOne")
        self.assertEqual(node.mutations[0].index, [4])

    def testFindWordCap(self):
        node = self.getNext("findWord", "rOBert")
        self.assertEqual(node.word, "robert")
        self.assertEqual(node.type, "word")
        self.assertEqual(node.mutations[0].type, "caseMulti")
        self.assertEqual(node.mutations[0].index, [1, 2])

        node = self.getNext("findWord", "Elephant")
        self.assertEqual(node.word, "elephant")
        self.assertEqual(node.type, "word")
        self.assertEqual(node.mutations[0].type, "caseFirst")
        self.assertEqual(node.mutations[0].index, [0])

        node = self.getNext("findWord", "poRk")
        self.assertEqual(node.word, "pork")
        self.assertEqual(node.type, "word")
        self.assertEqual(node.mutations[0].type, "caseOne")
        self.assertEqual(node.mutations[0].index, [2])

    def testFindWordCapFail(self):
        node = self.getNext("findWord", "rich")
        self.assertEqual(node.word, "rich")
        self.assertEqual(node.type, "word")
        self.assertListEqual(node.mutations, [])

    def testFindWordCapMultiLeetMulti(self):
        node = self.getNext("findWord", "T3l3gr4PH")
        self.assertEqual(node.word, "telegraph")
        self.assertEqual(node.type, "word")
        self.assertEqual(node.mutations[0].type, "caseMulti")
        self.assertEqual(node.mutations[0].index, [0, 7, 8])
        self.assertEqual(node.mutations[1].type, "leetMulti")
        self.assertEqual(node.mutations[1].index, [1, 3, 6])

    def testFindDatePart(self):
        node = self.getNext("findDate", "102399842")
        self.assertEqual(node.word, "102399")
        self.assertEqual(node.type, "date")
        self.assertEqual(node.mutations, [])

    def testFindDateYMD(self):
        node = self.getNext("findDate", "2009/04/21")
        self.assertEqual(node.word, "2009/04/21")
        self.assertEqual(node.type, "date")
        self.assertEqual(node.mutations, [])

    def testFindDateMon(self):
        node = self.getNext("findDate", "2009/mar/21")
        self.assertEqual(node.word, "2009/mar/21")
        self.assertEqual(node.type, "date")
        self.assertEqual(node.mutations, [])
        node = self.getNext("findDate", "Sep/21")
        self.assertEqual(node.word, "Sep/21")
        self.assertEqual(node.type, "date")
        self.assertEqual(node.mutations, [])
        node = self.getNext("findDate", "1941-Aug")
        self.assertEqual(node.word, "1941-Aug")
        self.assertEqual(node.type, "date")
        self.assertEqual(node.mutations, [])

    def testFindDateMonth(self):
        node = self.getNext("findDate", "2009/March/21")
        self.assertEqual(node.word, "2009/March/21")
        self.assertEqual(node.type, "date")
        self.assertEqual(node.mutations, [])
        node = self.getNext("findDate", "21/September")
        self.assertEqual(node.word, "21/September")
        self.assertEqual(node.type, "date")
        self.assertEqual(node.mutations, [])
        node = self.getNext("findDate", "August24")
        self.assertEqual(node.word, "August24")
        self.assertEqual(node.type, "date")
        self.assertEqual(node.mutations, [])

    def testFindDateYM(self):
        node = self.getNext("findDate", "200809")
        self.assertEqual(node.word, "200809")
        self.assertEqual(node.type, "date")
        self.assertEqual(node.mutations, [])

    def testFindDateMD(self):
        node = self.getNext("findDate", "01.20")
        self.assertEqual(node.word, "01.20")
        self.assertEqual(node.type, "date")
        self.assertEqual(node.mutations, [])

    def testFindDateY(self):
        node = self.getNext("findDate", "1949")
        self.assertEqual(node.word, "1949")
        self.assertEqual(node.type, "date")
        self.assertEqual(node.mutations, [])

    def testFindDateFail(self):
        node = self.getNext("findDate", "1900")
        self.assertNotEqual(node.type, "date")

    def testFindRepeated(self):
        node = self.getNext("findRepeated", "twolllllllthree")
        self.assertEqual(node.word, "two")
        self.assertEqual(node.next[0].word, "lllllll")
        self.assertEqual(node.next[0].type, "repetition")

    def testFindRepeatedFail(self):
        node = self.getNext("findRepeated", "201948")
        self.assertNotEqual(node.type, "repetition")

    def testFindEmail(self):
        node = self.getNext("findEmail", "dsapwqa.320@iatz.net")
        self.assertEqual(node.word, "dsapwqa.320@iatz.net")
        self.assertEqual(node.type, "email")

    def testFindEmailFail(self):
        node = self.getNext("findEmail", "dsapwqa.320@ca")
        self.assertNotEqual(node.type, "email")

    def testFindKeyRun(self):
        node = self.getNext("findKeyRun", "sdfghjkl")
        self.assertEqual(node.word, "sdfghjkl")
        self.assertEqual(node.type, "keyboard")
        self.assertEqual(node.cost, 264)

    def testFindKeyRunBreaks(self):
        node = self.getNext("findKeyRun", "123456qwerty")
        self.assertEqual(node.word, "123456qwerty")
        self.assertEqual(node.type, "keyboard")
        self.assertEqual(node.cost, 264**2)

    def testFindKeyRunFail(self):
        node = self.getNext("findKeyRun", "pqowieuryt")
        self.assertNotEqual(node.type, "keyboard")

    def testFindBruteForce(self):
        node = self.getNext("findBruteForce", "owirudyas")
        self.assertEqual(node.word, "owirudyas")
        self.assertEqual(node.type, "bruteforce-lowercase")
        self.assertEqual(node.cost, 26 ** 9)

        node = self.getNext("findBruteForce", "94532")
        self.assertEqual(node.word, "94532")
        self.assertEqual(node.type, "bruteforce-digits")
        self.assertEqual(node.cost, 10 ** 5)

        node = self.getNext("findBruteForce", "94$532")
        self.assertEqual(node.word, "94$532")
        self.assertEqual(node.type, "bruteforce")
        self.assertEqual(node.cost, 72 ** 6)

        node = self.getNext("findBruteForce", "CEPQOSWA")
        self.assertEqual(node.word, "CEPQOSWA")
        self.assertEqual(node.type, "bruteforce")
        self.assertEqual(node.cost, 26 ** 8)

class TestRemove(unittest.TestCase):
    def testRemoveCase(self):
        pw = pass_check.Password("aAaAaaAAaAA")
        word, mutation = pw.removeCase(pw.root.next[0].word)
        self.assertEqual(word, "aaaaaaaaaaa")
        self.assertEqual(mutation.type, "caseMulti")
        self.assertEqual(mutation.index, [1, 3, 6, 7, 9, 10])

        pw = pass_check.Password("34a90ReElo@A")
        word, mutation = pw.removeCase(pw.root.next[0].word)
        self.assertEqual(word, "34a90reelo@a")
        self.assertEqual(mutation.type, "caseMulti")
        self.assertEqual(mutation.index, [5, 7, 11])

    def testRemoveLeet(self):
        pw = pass_check.Password("0mg")
        for word, mutation in pw.removeLeet(pw.root.next[0].word):
            self.assertEqual(word, "omg")
            self.assertEqual(mutation.type, "leetOne")
            self.assertEqual(mutation.index, [0])

        pw = pass_check.Password("!ll!n0i5")
        for word, mutation in pw.removeLeet(pw.root.next[0].word):
            self.assertEqual(word, "illinois")
            self.assertEqual(mutation.type, "leetMulti")
            self.assertEqual(mutation.index, [0,3,5,7])

    def testRemoveDelimiter(self):
        pw = pass_check.Password("p-a-s-s-w-o-r-d")
        word, mutation = pw.removeDelimiter(pw.root.next[0].word)
        self.assertEqual(word, "password")
        self.assertEqual(mutation.type, "delimiter")
        self.assertEqual(mutation.index, [1,3,5,7,9,11,13])

        pw = pass_check.Password("-l-i-s-a-")
        word, mutation = pw.removeDelimiter(pw.root.next[0].word)
        self.assertEqual(word, "lisa")
        self.assertEqual(mutation.type, "delimiter")
        self.assertEqual(mutation.index, [0,2,4,6,8])

        pw = pass_check.Password(".n.o.t.g.o.o.d2008")
        word, mutation = pw.removeDelimiter(pw.root.next[0].word)
        self.assertEqual(word, "notgood2008")
        self.assertEqual(mutation.type, "delimiter")
        self.assertEqual(mutation.index, [0,2,4,6,8,10,12])

        pw = pass_check.Password(" h i m o m")
        word, mutation = pw.removeDelimiter(pw.root.next[0].word)
        self.assertEqual(word, "himom")
        self.assertEqual(mutation.type, "delimiter")
        self.assertEqual(mutation.index, [0,2,4,6,8])

        pw = pass_check.Password("f_a_il")
        word, mutation = pw.removeDelimiter(pw.root.next[0].word)
        self.assertEqual(word, "f_a_il")
        self.assertEqual(mutation, None)

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
            pw.root.next[0].word, minLength=3)):
            self.assertEqual(expected[index], (prefix, suffix, sub))

        pw = pass_check.Password("seven")
        expected = [
            ("", "", "seven"),
            ("", "n", "seve"),
            ("s", "", "even")
        ]
        for index, (prefix, suffix, sub) in enumerate(pw.subPermutations(
            pw.root.next[0].word, minLength=4)):
            self.assertEqual(expected[index], (prefix, suffix, sub))

class TestCombined(unittest.TestCase):
    """Documentation for ideal cases. These may fail until problems are
    solved, or wordlists are finalized."""
    def testBorderConflict(self):
        """Tests that conflicts between borders and leet replacements are
        handled properly. Should read $$money$$ instead of $$moneys$."""
        pc = pass_check.PassCheck("$$money$$")
        pc.findParts()
        pc.findLowestCost()
        self.assertEqual(pc.finalParts[0].word, "$$")
        self.assertEqual(pc.finalParts[0].type, 'repetition')
        self.assertEqual(pc.finalParts[0].mutations, [])
        self.assertEqual(pc.finalParts[0].pattern, 'border-repeat')
        self.assertEqual(pc.finalParts[1].word, "money")
        self.assertEqual(pc.finalParts[1].type, 'word')
        self.assertEqual(pc.finalParts[1].mutations, [])
        self.assertEqual(pc.finalParts[1].pattern, None)
        self.assertEqual(pc.finalParts[2].word, "$$")
        self.assertEqual(pc.finalParts[2].type, 'repetition')
        self.assertEqual(pc.finalParts[2].mutations, [])
        self.assertEqual(pc.finalParts[2].pattern, 'border-repeat')

    def testMultipleBorders(self):
        """Tests two borders with an identical delimiter (should be picked up as
        a single border with delimiter between two dictionary words)"""
        pc = pass_check.PassCheck("!!tim!!tammy!!")
        pc.findParts()
        pc.findLowestCost()
        self.assertEqual(pc.finalParts[0].word, "!!")
        self.assertEqual(pc.finalParts[0].type, 'repetition')
        self.assertEqual(pc.finalParts[0].mutations, [])
        self.assertEqual(pc.finalParts[0].pattern, 'border-repeat')
        self.assertEqual(pc.finalParts[1].word, "tim")
        self.assertEqual(pc.finalParts[1].type, 'word')
        self.assertEqual(pc.finalParts[1].mutations, [])
        self.assertEqual(pc.finalParts[1].pattern, 'word-combination')
        self.assertEqual(pc.finalParts[2].word, "!!")
        self.assertEqual(pc.finalParts[2].type, 'repetition')
        self.assertEqual(pc.finalParts[2].mutations, [])
        self.assertEqual(pc.finalParts[2].pattern, 'word-combination-delimiter')
        self.assertEqual(pc.finalParts[3].word, "tammy")
        self.assertEqual(pc.finalParts[3].type, 'word')
        self.assertEqual(pc.finalParts[3].mutations, [])
        self.assertEqual(pc.finalParts[3].pattern, 'word-combination')
        self.assertEqual(pc.finalParts[4].word, "!!")
        self.assertEqual(pc.finalParts[4].type, 'repetition')
        self.assertEqual(pc.finalParts[4].mutations, [])
        self.assertEqual(pc.finalParts[4].pattern, 'border-repeat')
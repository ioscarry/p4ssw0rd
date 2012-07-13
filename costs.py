"""
Mutations:
Upper/lower shifts                                              *
    All upper                                                   * 2             LAGOS, SARA
    First upper                                                 + 1             Losangeles, Password
    Single random upper                                         + 6             waIting, batTle
l33t mutations                                                  * 32            r!7u4l, 31iz@b3th
Delimiters between letters, with and without borders: '-_.= '   * 20            p-a-s-s-w-o-r-d-, .e.l.i.z.a.
Swap 2 adjacent characters                                      * (len-1) ^ 2   apssword
Missing 2 characters                                            * (len-1) ^ 2   pssword
Duplicated 2 characters (ppaassword)                            * (len-1) ^ 2   paassword

Append:
One common symbol											    + 10			lol$, tammy!
Uncommon symbol                                                 + 22            tiffany|, ouchie=
Duplicated numbers 11 through 9999                              + 40            luvu22, omgevil66
Inclusive runs from 1234567890, including rotate                + 50            date23456789, pass89012345
Numbers 1940-2015                                               + 75            jim1949, arcane2012
Numbers 0-9 and 00-99                                           + 110           password1, douglas42
Common symbol repeated 1-3 times                                + 30            princess@@, wow!
Uncommon symbol repeated 1-3 times                              + 66            hithere>>, ffffffffff|||
Common border symbol repeated 1-3 times                         + 30            ((store)), $$$money$$$
Uncommon border symbol repeated 1-3 times                       + 66            <<store>>, /path/
One symbol plus numbers 0-9 and 00-99                           + 262           password$42, tent!22
Numbers in date patterns, 1940-2015
    DD/MM/YYYY (/-. )                                           * 164250        esmeralda30081994
    DD/MM/YY                                                    + 164250        john30/01/82
    D/M/YYYY                                                    + 104625        state1/4/2012
    D/M/YY                                                      + 104625        password4510
    MM/DD/YYYY                                                  + 164250        wreck02/03/2001
    MM/DD/YY                                                    + 164250        planes09-07-91
    M/D/YYYY                                                    + 104625        born1/14/1949
    M/D/YY                                                      + 104625        slow3.21.1974
    YYYY/MM/DD                                                  + 164250        gem2008/10/30
    YY/MM/DD                                                    + 164250        ursula121201
    YYYY/M/D                                                    + 104625         air2008/11/08
    YY/M/D                                                      + 104625         exhibit82614
    MM/YYYY                                                     + 5400          horrified092000
    MM/YY                                                       + 5400          drastic0599
    YYYY/MM                                                     + 5400          loud199208
    YY/MM                                                       + 5400          tonight04-49
    M/YYYY                                                      + 4050          happily1.2001
    M/YY                                                        + 4050          nearby9-60
    YYYY/M                                                      + 4050          counter1957-4
    YY/M                                                        + 4050          rightly72/5
Numbers added to 8 char                                         * 111111111     num980110924, 098792today
Numbers and symbols added to 8 char                             * 9900000000000 arg102$2!08, !!@#^$&9hello
"""

# Costs of all mutations
mutations = {
    "caseFirst":    2,
    "caseUpper":    3,
    "caseOne":      6,
    "caseMulti":    32,
    "leetOne":      6,
    "leetMulti":    32,
    "delimiter":    20,
    "swapOne":      6,
    "swapMulti":    36,
    "missingOne":   6,
    "missingMulti": 36,
    "dupeOne":      6,
    "dupeMulti":    36,
}

# Cumulative costs for mutations
mutations = {
    "caseFirst": 2,
    "caseUpper": 5,
    "caseOne": 11,
    "dupeOne": 17,
    "leetOne": 23,
    "missingOne": 29,
    "swapOne": 35,
    "delimiter": 55,
    "caseMulti": 87,
    "leetMulti": 119,
    "dupeMulti": 155,
    "missingMulti": 191,
    "swapMulti": 227,
}

# Costs of appending to a base word or combination word
append = {
    "symbolOneCommon":          10,
    "symbolOneUncommon":        22,
    "number11to9999":           40,
    "numberRun":                50,
    "number0-99":               110,
    "symbol2to3Common":         30,
    "symbol2to3Uncommon":       66,
    "borderRepeatCommon1to3":   30,
    "borderRepeatUncommon1to3": 66,
    "dateY":                    75,
    "dateYM":                   37800,
    "dateYMD":                  1613250,
    "numbers3to6":              1111000,
    "numbers7to8":              110000000,
    "numbersSymbols1to8":       9900000000000,
}

if __name__ == "__main__":
    maxValue = 0
    print "mutations = {"
    for key, value in sorted(mutations.iteritems(), key=lambda(k, v): (v, k)):
        maxValue += value
        print '\t"{}": {},'.format(key, maxValue)
    print "}"

#    maxValue = 0
#    print "append = {"
#    for key, value in sorted(append.iteritems(), key=lambda(k, v): (v, k)):
#        maxValue += value
#        print '\t"{}": {},'.format(key, maxValue)
#    print "}"
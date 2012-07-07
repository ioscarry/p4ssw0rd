"""
Sources:
ftp://ftp.openwall.com/pub/wordlists/
http://www.skullsecurity.org/wiki/index.php/Passwords
http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists
http://contest-2010.korelogic.com/wordlists.html
"""

import os, re, mmap, string
import binary_search
import cProfile

regexNotLowercase = re.compile("[^a-z]")
regexNotLowercaseApostrophe = re.compile("[^a-z']")

type = ['letter','digit','letterapostrophe','combined']
wordPath = "words"
workPath = os.path.join("words", "work")

# Defines the order in which wordlists are searched - used for convertFiles only
wordsOrder = [
    "openwall-password.dic",
    "rockyou_top1000.dic",
    "numbers_as_words.dic",
    "names.dic",
    "tv-1-5000-special.dic",
    "tv-1-5000.dic",
    "tv-5000-10000-special.dic",
    "tv-5000-10000.dic",
    "english-tiny-cap.dic",
    "english-tiny-lower.dic",
    "contemporaryfiction-special.dic",
    "contemporaryfiction.dic",
    "bible_books.dic",
    "cities.dic",
    "places.dic",
    "english-small-alnum.dic",
    "english-small-cap.dic",
    "english-small-lower.dic",
    "english-small-mixed.dic",
    "sports.dic",
    "sports_proteams.dic",
#    "english-large-acronym.dic",
#    "english-large-alnum.dic",
#    "english-large-cap.dic",
#    "english-large-lower.dic",
#    "english-large-mixed.dic",
#    "english-extra-acronym.dic",
#    "english-extra-alnum.dic",
#    "english-extra-cap.dic",
#    "english-extra-lower.dic",
#    "english-extra-mixed.dic",
]

wordFiles = {
    1:{"name":"1.dic", "handle":None, "letterIndex":{'*': (0, 5), '1': (5, 11), 'I': (11, 20), '_': (20, 27), 'a': (27, 34), 'c': (43, 52), 'b': (34, 43), 'e': (61, 69), 'd': (52, 61), 'g': (78, 87), 'f': (69, 78), 'i': (96, 105), 'h': (87, 96), 'k': (114, 123), 'j': (105, 114), 'm': (132, 141), 'l': (123, 132), 'o': (150, 159), 'n': (141, 150), 'q': (168, 177), 'p': (159, 168), 's': (186, 195), 'r': (177, 186), 'u': (204, 213), 't': (195, 204), 'w': (222, 231), 'v': (213, 222), 'y': (240, 249), 'x': (231, 240), 'z': (249, 258)}},
    10:{"name":"10.dic", "handle":None, "letterIndex":{'1': (34, 51), '0': (0, 34), 'A': (51, 5694), 'C': (9399, 15973), 'B': (5694, 9399), 'E': (18177, 20590), 'D': (15973, 18177), 'G': (21882, 24333), 'F': (20590, 21882), 'I': (27259, 28171), 'H': (24333, 27259), 'K': (28988, 29976), 'J': (28171, 28988), 'M': (32218, 36246), 'L': (29976, 32218), 'O': (37690, 39115), 'N': (36246, 37690), 'Q': (45898, 46069), 'P': (39115, 45898), 'S': (47722, 53346), 'R': (46069, 47722), 'U': (56956, 57222), 'T': (53346, 56956), 'W': (58153, 59160), 'V': (57222, 58153), 'Y': (59369, 59559), 'X': (59160, 59369), 'Z': (59559, 59901), 'a': (59901, 110411), 'c': (145693, 210921), 'b': (110411, 145693), 'e': (248964, 279582), 'd': (210921, 248964), 'g': (303627, 323600), 'f': (279582, 303627), 'i': (351452, 380248), 'h': (323600, 351452), 'k': (384085, 389092), 'j': (380248, 384085), 'm': (406981, 450211), 'l': (389092, 406981), 'o': (468760, 496591), 'n': (450211, 468760), 'q': (570920, 573965), 'p': (496591, 570920), 's': (609489, 690823), 'r': (573965, 609489), 'u': (726778, 778638), 't': (690823, 726778), 'w': (789675, 803827), 'v': (778638, 789675), 'y': (804870, 805968), 'x': (803827, 804870), 'z': (805968, 807792)}},
    11:{"name":"11.dic", "handle":None, "letterIndex":{'1': (0, 18), 'A': (18, 4418), 'C': (6498, 12218), 'B': (4418, 6498), 'E': (14038, 15898), 'D': (12218, 14038), 'G': (16838, 18638), 'F': (15898, 16838), 'I': (21258, 22058), 'H': (18638, 21258), 'K': (22578, 22998), 'J': (22058, 22578), 'M': (24778, 28298), 'L': (22998, 24778), 'O': (29378, 30378), 'N': (28298, 29378), 'Q': (36518, 36598), 'P': (30378, 36518), 'S': (37638, 42118), 'R': (36598, 37638), 'U': (44738, 44978), 'T': (42118, 44738), 'W': (45458, 46038), 'V': (44978, 45458), 'Y': (46278, 46398), 'X': (46038, 46278), 'Z': (46398, 46658), 'a': (46658, 90070), 'c': (114438, 172640), 'b': (90070, 114438), 'e': (203142, 227995), 'd': (172640, 203142), 'g': (245345, 259992), 'f': (227995, 245345), 'i': (284544, 313613), 'h': (259992, 284544), 'k': (315901, 319074), 'j': (313613, 315901), 'm': (332546, 367852), 'l': (319074, 332546), 'o': (387315, 410095), 'n': (367852, 387315), 'q': (480948, 483477), 'p': (410095, 480948), 's': (512180, 573939), 'r': (483477, 512180), 'u': (603844, 651613), 't': (573939, 603844), 'w': (660370, 670340), 'v': (651613, 660370), 'y': (671199, 671758), 'x': (670340, 671199), 'z': (671758, 673076)}},
    12:{"name":"12.dic", "handle":None, "letterIndex":{'A': (0, 2961), 'C': (4221, 8022), 'B': (2961, 4221), 'E': (9345, 10731), 'D': (8022, 9345), 'G': (11172, 12474), 'F': (10731, 11172), 'I': (14763, 15288), 'H': (12474, 14763), 'K': (15666, 15834), 'J': (15288, 15666), 'M': (17262, 19866), 'L': (15834, 17262), 'O': (20916, 21903), 'N': (19866, 20916), 'Q': (26355, 26418), 'P': (21903, 26355), 'S': (27489, 31017), 'R': (26418, 27489), 'U': (33264, 33579), 'T': (31017, 33264), 'W': (33957, 34272), 'V': (33579, 33957), 'Y': (34587, 34671), 'X': (34272, 34587), 'Z': (34671, 35028), 'a': (35028, 68315), 'c': (83086, 128146), 'b': (68315, 83086), 'e': (153407, 174399), 'd': (128146, 153407), 'g': (186174, 196216), 'f': (174399, 186174), 'i': (216698, 244919), 'h': (196216, 216698), 'k': (246195, 248377), 'j': (244919, 246195), 'm': (257292, 286478), 'l': (248377, 257292), 'o': (304693, 321387), 'n': (286478, 304693), 'q': (380155, 382585), 'p': (321387, 380155), 's': (404142, 454700), 'r': (382585, 404142), 'u': (477734, 521106), 't': (454700, 477734), 'w': (527210, 532826), 'v': (521106, 527210), 'y': (533309, 533729), 'x': (532826, 533309), 'z': (533729, 534631)}},
    13:{"name":"13.dic", "handle":None, "letterIndex":{'A': (0, 2112), 'C': (2948, 5984), 'B': (2112, 2948), 'E': (6798, 7766), 'D': (5984, 6798), 'G': (8096, 8954), 'F': (7766, 8096), 'I': (10450, 10802), 'H': (8954, 10450), 'K': (11044, 11176), 'J': (10802, 11044), 'M': (12122, 13750), 'L': (11176, 12122), 'O': (14344, 14894), 'N': (13750, 14344), 'Q': (18260, 18348), 'P': (14894, 18260), 'S': (18832, 21164), 'R': (18348, 18832), 'U': (22924, 22990), 'T': (21164, 22924), 'W': (23210, 23386), 'V': (22990, 23210), 'Y': (23452, 23474), 'X': (23386, 23452), 'Z': (23474, 23694), 'a': (23694, 47595), 'c': (57624, 91117), 'b': (47595, 57624), 'e': (108961, 123886), 'd': (91117, 108961), 'g': (130942, 137685), 'f': (123886, 130942), 'i': (152023, 174826), 'h': (137685, 152023), 'k': (175702, 177217), 'j': (174826, 175702), 'm': (183857, 205054), 'l': (177217, 183857), 'o': (222087, 236224), 'n': (205054, 222087), 'q': (286494, 288797), 'p': (236224, 286494), 's': (305040, 340255), 'r': (288797, 305040), 'u': (356126, 387444), 't': (340255, 356126), 'w': (391638, 393967), 'v': (387444, 391638), 'y': (394538, 394802), 'x': (393967, 394538), 'z': (394802, 395550)}},
    14:{"name":"14.dic", "handle":None, "letterIndex":{'A': (0, 1334), 'C': (2024, 3818), 'B': (1334, 2024), 'E': (4324, 4830), 'D': (3818, 4324), 'G': (5060, 5612), 'F': (4830, 5060), 'I': (6647, 6808), 'H': (5612, 6647), 'J': (6808, 6854), 'M': (7130, 8165), 'L': (6854, 7130), 'O': (8441, 8901), 'N': (8165, 8441), 'P': (8901, 11247), 'S': (11661, 12949), 'R': (11247, 11661), 'U': (13800, 13892), 'T': (12949, 13800), 'W': (14030, 14145), 'V': (13892, 14030), 'X': (14145, 14168), 'Z': (14168, 14329), 'a': (14329, 32647), 'c': (37764, 58589), 'b': (32647, 37764), 'e': (70673, 80161), 'd': (58589, 70673), 'g': (84273, 88019), 'f': (80161, 84273), 'i': (98011, 113447), 'h': (88019, 98011), 'k': (113838, 114390), 'j': (113447, 113838), 'm': (118115, 131788), 'l': (114390, 118115), 'o': (144593, 154458), 'n': (131788, 144593), 'q': (188827, 190826), 'p': (154458, 188827), 's': (202203, 228514), 'r': (190826, 202203), 'u': (239691, 262375), 't': (228514, 239691), 'w': (264880, 266557), 'v': (262375, 264880), 'y': (266902, 266971), 'x': (266557, 266902), 'z': (266971, 267385)}},
    15:{"name":"15.dic", "handle":None, "letterIndex":{'A': (0, 744), 'C': (1080, 2328), 'B': (744, 1080), 'E': (2520, 2784), 'D': (2328, 2520), 'G': (2904, 3096), 'F': (2784, 2904), 'I': (3504, 3624), 'H': (3096, 3504), 'K': (3720, 3744), 'J': (3624, 3720), 'M': (4008, 4704), 'L': (3744, 4008), 'O': (4824, 4992), 'N': (4704, 4824), 'P': (4992, 6528), 'S': (6672, 7656), 'R': (6528, 6672), 'U': (8016, 8088), 'T': (7656, 8016), 'V': (8088, 8160), 'Z': (8160, 8232), 'a': (8232, 19076), 'c': (22866, 36125), 'b': (19076, 22866), 'e': (43682, 49988), 'd': (36125, 43682), 'g': (52171, 54235), 'f': (49988, 52171), 'i': (61046, 72269), 'h': (54235, 61046), 'k': (72458, 72770), 'j': (72269, 72458), 'm': (74810, 83136), 'l': (72770, 74810), 'o': (91388, 97748), 'n': (83136, 91388), 'q': (120583, 121733), 'p': (97748, 120583), 's': (127324, 143997), 'r': (121733, 127324), 'u': (151092, 164812), 't': (143997, 151092), 'w': (165940, 166828), 'v': (164812, 165940), 'y': (166972, 167020), 'x': (166828, 166972), 'z': (167020, 167236)}},
    16:{"name":"16.dic", "handle":None, "letterIndex":{'A': (0, 300), 'C': (475, 1075), 'B': (300, 475), 'E': (1225, 1375), 'D': (1075, 1225), 'G': (1375, 1400), 'I': (1625, 1675), 'H': (1400, 1625), 'J': (1675, 1700), 'M': (1775, 2200), 'L': (1700, 1775), 'O': (2200, 2275), 'P': (2275, 2825), 'S': (2925, 3500), 'R': (2825, 2925), 'T': (3500, 3700), 'W': (3775, 3825), 'V': (3700, 3775), 'Z': (3825, 3875), 'a': (3875, 10197), 'c': (12071, 20765), 'b': (10197, 12071), 'e': (24514, 27912), 'd': (20765, 24514), 'g': (28712, 29861), 'f': (27912, 28712), 'i': (34011, 41280), 'h': (29861, 34011), 'k': (41405, 41580), 'j': (41280, 41405), 'm': (42705, 47878), 'l': (41580, 42705), 'o': (52203, 55527), 'n': (47878, 52203), 'q': (69725, 70175), 'p': (55527, 69725), 's': (72899, 82774), 'r': (70175, 72899), 'u': (87169, 96542), 't': (82774, 87169), 'w': (97192, 97667), 'v': (96542, 97192), 'x': (97667, 97717), 'z': (97717, 97792)}},
    17:{"name":"17.dic", "handle":None, "letterIndex":{'A': (0, 208), 'C': (286, 572), 'B': (208, 286), 'E': (650, 728), 'D': (572, 650), 'G': (728, 780), 'H': (780, 858), 'M': (910, 1118), 'L': (858, 910), 'O': (1144, 1222), 'N': (1118, 1144), 'P': (1222, 1560), 'S': (1612, 1820), 'R': (1560, 1612), 'T': (1820, 1950), 'Z': (1950, 1976), 'a': (1976, 5434), 'c': (6448, 11642), 'b': (5434, 6448), 'e': (13774, 15983), 'd': (11642, 13774), 'g': (16269, 16789), 'f': (15983, 16269), 'i': (19467, 23521), 'h': (16789, 19467), 'k': (23625, 23781), 'j': (23521, 23625), 'm': (24717, 27499), 'l': (23781, 24717), 'o': (29865, 31709), 'n': (27499, 29865), 'q': (39925, 40237), 'p': (31709, 39925), 's': (41641, 46763), 'r': (40237, 41641), 'u': (49127, 53884), 't': (46763, 49127), 'w': (54274, 54456), 'v': (53884, 54274), 'z': (54456, 54560)}},
    18:{"name":"18.dic", "handle":None, "letterIndex":{'A': (0, 54), 'C': (81, 297), 'B': (54, 81), 'E': (297, 324), 'H': (324, 405), 'M': (432, 486), 'L': (405, 432), 'P': (486, 648), 'S': (675, 729), 'R': (648, 675), 'a': (729, 2564), 'c': (3239, 5803), 'b': (2564, 3239), 'e': (6667, 7881), 'd': (5803, 6667), 'g': (8015, 8393), 'f': (7881, 8015), 'i': (9905, 11876), 'h': (8393, 9905), 'j': (11876, 11903), 'm': (12227, 13334), 'l': (11903, 12227), 'o': (14144, 15440), 'n': (13334, 14144), 'q': (19625, 19733), 'p': (15440, 19625), 's': (20138, 22865), 'r': (19733, 20138), 'u': (24483, 26508), 't': (22865, 24483), 'w': (26724, 26886), 'v': (26508, 26724), 'z': (26886, 26994)}},
    19:{"name":"19.dic", "handle":None, "letterIndex":{'C': (0, 56), 'E': (56, 84), 'I': (168, 196), 'H': (84, 168), 'M': (196, 252), 'P': (252, 308), 'a': (308, 1288), 'c': (1735, 3134), 'b': (1288, 1735), 'e': (3582, 4449), 'd': (3134, 3582), 'g': (4533, 4813), 'f': (4449, 4533), 'i': (5709, 6548), 'h': (4813, 5709), 'm': (6772, 7332), 'l': (6548, 6772), 'o': (7500, 8255), 'n': (7332, 7500), 'p': (8255, 10495), 's': (10691, 11783), 'r': (10495, 10691), 'u': (12203, 13491), 't': (11783, 12203), 'w': (13519, 13547), 'v': (13491, 13519), 'z': (13547, 13603)}},
    2:{"name":"2.dic", "handle":None, "letterIndex":{'3': (11, 22), '2': (0, 11), 'A': (22, 88), 'C': (99, 110), 'B': (88, 99), 'E': (132, 165), 'D': (110, 132), 'G': (198, 231), 'F': (165, 198), 'I': (264, 286), 'H': (231, 264), 'K': (319, 352), 'J': (286, 319), 'M': (385, 440), 'L': (352, 385), 'O': (440, 495), 'Q': (517, 528), 'P': (495, 517), 'S': (572, 605), 'R': (528, 572), 'U': (616, 627), 'T': (605, 616), 'W': (638, 660), 'V': (627, 638), 'a': (660, 868), 'c': (1016, 1184), 'b': (868, 1016), 'e': (1318, 1504), 'd': (1184, 1318), 'g': (1610, 1695), 'f': (1504, 1610), 'i': (1795, 1960), 'h': (1695, 1795), 'k': (2027, 2144), 'j': (1960, 2027), 'm': (2301, 2509), 'l': (2144, 2301), 'o': (2680, 2866), 'n': (2509, 2680), 'q': (3046, 3090), 'p': (2866, 3046), 's': (3186, 3353), 'r': (3090, 3186), 'u': (3500, 3593), 't': (3353, 3500), 'w': (3665, 3792), 'v': (3593, 3665), 'y': (3898, 4003), 'x': (3792, 3898), 'z': (4003, 4047)}},
    20:{"name":"20.dic", "handle":None, "letterIndex":{'A': (0, 29), 'C': (58, 87), 'B': (29, 58), 'M': (87, 116), 'a': (116, 841), 'c': (1044, 1711), 'b': (841, 1044), 'e': (1914, 2291), 'd': (1711, 1914), 'g': (2291, 2407), 'i': (2929, 3277), 'h': (2407, 2929), 'k': (3277, 3306), 'm': (3451, 3712), 'l': (3306, 3451), 'o': (3915, 4205), 'n': (3712, 3915), 'p': (4205, 5481), 's': (5626, 6206), 'r': (5481, 5626), 'u': (6525, 6931), 't': (6206, 6525), 'w': (6960, 7047), 'v': (6931, 6960), 'y': (7047, 7076)}},
    21:{"name":"21.dic", "handle":None, "letterIndex":{'a': (30, 360), 'c': (390, 900), 'b': (360, 390), 'e': (1080, 1230), 'd': (900, 1080), 'g': (1260, 1350), 'f': (1230, 1260), 'i': (1530, 1680), 'h': (1350, 1530), 'j': (1680, 1710), 'm': (1740, 1980), 'l': (1710, 1740), 'o': (2010, 2070), 'n': (1980, 2010), 'P': (0, 30), 's': (2640, 2820), 'u': (2910, 2970), 't': (2820, 2910), 'y': (2970, 3000), 'z': (3000, 3030), 'p': (2070, 2640)}},
    22:{"name":"22.dic", "handle":None, "letterIndex":{'a': (31, 93), 'c': (124, 310), 'b': (93, 124), 'e': (465, 558), 'd': (310, 465), 'f': (558, 589), 'h': (589, 744), 'k': (744, 775), 'm': (837, 868), 'l': (775, 837), 'o': (930, 961), 'n': (868, 930), 'P': (0, 31), 's': (1240, 1302), 'u': (1395, 1426), 't': (1302, 1395), 'z': (1426, 1457), 'p': (961, 1240)}},
    23:{"name":"23.dic", "handle":None, "letterIndex":{'a': (32, 64), 'b': (64, 96), 'e': (128, 192), 'd': (96, 128), 'g': (256, 288), 'f': (192, 256), 'h': (288, 352), 'k': (352, 384), 'm': (384, 480), 'p': (480, 672), 's': (672, 704), 'u': (768, 800), 't': (704, 768), 'w': (800, 832), 'P': (0, 32)}},
    24:{"name":"24.dic", "handle":None, "letterIndex":{'p': (33, 66), 's': (66, 132), 'u': (198, 231), 't': (132, 198), 'f': (0, 33)}},
    25:{"name":"25.dic", "handle":None, "letterIndex":{'a': (0, 34), 'c': (34, 68)}},
    26:{"name":"26.dic", "handle":None, "letterIndex":{'t': (0, 0)}},
    28:{"name":"28.dic", "handle":None, "letterIndex":{'a': (0, 0)}},
    29:{"name":"29.dic", "handle":None, "letterIndex":{'A': (0, 228), 'C': (266, 380), 'B': (228, 266), 'E': (494, 646), 'D': (380, 494), 'G': (836, 912), 'F': (646, 836), 'I': (950, 988), 'H': (912, 950), 'M': (1183, 1300), 'L': (988, 1183), 'O': (1378, 1417), 'N': (1300, 1378), 'P': (1417, 1456), 'S': (1612, 1846), 'R': (1456, 1612), 'T': (1846, 1885), 'W': (1924, 2119), 'V': (1885, 1924), 'a': (2119, 2704), 'c': (3016, 3912), 'b': (2704, 3016), 'e': (4185, 4536), 'd': (3912, 4185), 'g': (4770, 5238), 'f': (4536, 4770), 'i': (5706, 6018), 'h': (5238, 5706), 'k': (6057, 6291), 'j': (6018, 6057), 'm': (6876, 7344), 'l': (6291, 6876), 'o': (7695, 7851), 'n': (7344, 7695), 'p': (7851, 8358), 's': (8553, 9255), 'r': (8358, 8553), 'u': (10775, 10970), 't': (9255, 10775), 'w': (11048, 11633), 'v': (10970, 11048), 'y': (11633, 11672)}},
    3:{"name":"3.dic", "handle":None, "letterIndex":{'1': (7, 27), '0': (0, 7), '3': (39, 59), '2': (27, 39), '5': (71, 83), '4': (59, 71), '7': (95, 115), '6': (83, 95), '9': (127, 147), '8': (115, 127), 'A': (147, 543), 'C': (747, 819), 'B': (543, 747), 'E': (987, 1082), 'D': (819, 987), 'G': (1202, 1369), 'F': (1082, 1202), 'I': (1441, 1657), 'H': (1369, 1441), 'K': (1824, 1968), 'J': (1657, 1824), 'M': (2290, 2613), 'L': (1968, 2290), 'O': (2721, 2889), 'N': (2613, 2721), 'Q': (3066, 3078), 'P': (2889, 3066), 'S': (3317, 3640), 'R': (3078, 3317), 'U': (3807, 3915), 'T': (3640, 3807), 'W': (3963, 4071), 'V': (3915, 3963), 'Y': (4071, 4119), 'Z': (4119, 4191), 'a': (4191, 5970), 'c': (6963, 8030), 'b': (5970, 6963), 'e': (9069, 10023), 'd': (8030, 9069), 'g': (10880, 11843), 'f': (10023, 10880), 'i': (12712, 13446), 'h': (11843, 12712), 'k': (13913, 14518), 'j': (13446, 13913), 'm': (15456, 16471), 'l': (14518, 15456), 'o': (17371, 18300), 'n': (16471, 17371), 'q': (19560, 19653), 'p': (18300, 19560), 's': (20593, 21944), 'r': (19653, 20593), 'u': (23198, 23814), 't': (21944, 23198), 'w': (24229, 24940), 'v': (23814, 24229), 'y': (25070, 25644), 'x': (24940, 25070), 'z': (25644, 25931)}},
    30:{"name":"30.dic", "handle":None, "letterIndex":{'A': (0, 117), 'C': (195, 312), 'B': (117, 195), 'E': (351, 507), 'D': (312, 351), 'G': (546, 585), 'F': (507, 546), 'I': (624, 819), 'H': (585, 624), 'M': (939, 1019), 'L': (819, 939), 'O': (1099, 1219), 'N': (1019, 1099), 'P': (1219, 1379), 'S': (1379, 1499), 'U': (1499, 1539), 'W': (1539, 1579), 'a': (1579, 2019), 'c': (2339, 2699), 'b': (2019, 2339), 'e': (2779, 3139), 'd': (2699, 2779), 'g': (3379, 3659), 'f': (3139, 3379), 'i': (4019, 4379), 'h': (3659, 4019), 'k': (4379, 4619), 'm': (4979, 5259), 'l': (4619, 4979), 'o': (5459, 5539), 'n': (5259, 5459), 'p': (5539, 6139), 's': (6259, 6779), 'r': (6139, 6259), 'u': (7819, 7859), 't': (6779, 7819), 'w': (7899, 8339), 'v': (7859, 7899), 'y': (8339, 8379)}},
    31:{"name":"31.dic", "handle":None, "letterIndex":{'A': (0, 200), 'C': (320, 440), 'B': (200, 320), 'E': (440, 640), 'G': (760, 800), 'F': (640, 760), 'I': (840, 1000), 'H': (800, 840), 'K': (1000, 1081), 'L': (1081, 1122), 'O': (1204, 1327), 'N': (1122, 1204), 'P': (1327, 1450), 'S': (1450, 1573), 'U': (1614, 1655), 'T': (1573, 1614), 'a': (1655, 2311), 'c': (2598, 3131), 'b': (2311, 2598), 'e': (3663, 3827), 'd': (3131, 3663), 'g': (4114, 4565), 'f': (3827, 4114), 'i': (5057, 5385), 'h': (4565, 5057), 'k': (5467, 5672), 'j': (5385, 5467), 'm': (6000, 6205), 'l': (5672, 6000), 'o': (6451, 6533), 'n': (6205, 6451), 'p': (6533, 6902), 's': (7025, 7476), 'r': (6902, 7025), 'u': (8419, 8542), 't': (7476, 8419), 'w': (8542, 8829), 'y': (8829, 8870)}},
    32:{"name":"32.dic", "handle":None, "letterIndex":{'A': (0, 123), 'C': (205, 369), 'B': (123, 205), 'E': (410, 451), 'D': (369, 410), 'G': (492, 615), 'F': (451, 492), 'I': (656, 738), 'H': (615, 656), 'K': (738, 904), 'O': (946, 988), 'N': (904, 946), 'S': (988, 1156), 'U': (1198, 1324), 'T': (1156, 1198), 'W': (1324, 1366), 'a': (1366, 1660), 'c': (1870, 2248), 'b': (1660, 1870), 'e': (2374, 2542), 'd': (2248, 2374), 'g': (2668, 2794), 'f': (2542, 2668), 'i': (3088, 3256), 'h': (2794, 3088), 'k': (3298, 3466), 'j': (3256, 3298), 'm': (3718, 3886), 'l': (3466, 3718), 'o': (4054, 4222), 'n': (3886, 4054), 'p': (4222, 4600), 's': (4684, 5104), 'r': (4600, 4684), 'u': (5860, 5986), 't': (5104, 5860), 'w': (5986, 6364)}},
    33:{"name":"33.dic", "handle":None, "letterIndex":{'I': (42, 84), 't': (84, 127), 'F': (0, 42)}},
    34:{"name":"34.dic", "handle":None, "letterIndex":{'i': (219, 263), 'S': (131, 219), 't': (263, 307), 'G': (0, 43), 'N': (43, 131)}},
    35:{"name":"35.dic", "handle":None, "letterIndex":{'c': (0, 0)}},
    36:{"name":"36.dic", "handle":None, "letterIndex":{'W': (0, 0)}},
    37:{"name":"37.dic", "handle":None, "letterIndex":{'I': (0, 46), 'i': (46, 93)}},
    39:{"name":"39.dic", "handle":None, "letterIndex":{'J': (0, 0)}},
    4:{"name":"4.dic", "handle":None, "letterIndex":{'1': (26, 93), '0': (0, 26), '2': (93, 111), '5': (120, 147), '4': (111, 120), '7': (169, 178), '6': (147, 169), 'A': (178, 1671), 'C': (2644, 3331), 'B': (1671, 2644), 'E': (3942, 4576), 'D': (3331, 3942), 'G': (4914, 5537), 'F': (4576, 4914), 'I': (6044, 6416), 'H': (5537, 6044), 'K': (6891, 7605), 'J': (6416, 6891), 'M': (8486, 9302), 'L': (7605, 8486), 'O': (9859, 10234), 'N': (9302, 9859), 'Q': (10817, 10830), 'P': (10234, 10817), 'S': (11464, 12488), 'R': (10830, 11464), 'U': (13267, 13488), 'T': (12488, 13267), 'W': (13735, 14085), 'V': (13488, 13735), 'Y': (14163, 14317), 'X': (14085, 14163), 'Z': (14317, 14447), 'a': (14447, 20359), 'c': (25834, 30797), 'b': (20359, 25834), 'e': (35339, 38458), 'd': (30797, 35339), 'g': (41884, 46066), 'f': (38458, 41884), 'i': (49821, 51743), 'h': (46066, 49821), 'k': (54020, 57384), 'j': (51743, 54020), 'm': (61727, 66411), 'l': (57384, 61727), 'o': (69363, 72261), 'n': (66411, 69363), 'q': (77425, 77885), 'p': (72261, 77425), 's': (82099, 89556), 'r': (77885, 82099), 'u': (94871, 96022), 't': (89556, 94871), 'w': (97667, 101128), 'v': (96022, 97667), 'y': (101317, 103248), 'x': (101128, 101317), 'z': (103248, 104154)}},
    40:{"name":"40.dic", "handle":None, "letterIndex":{'s': (0, 0)}},
    42:{"name":"42.dic", "handle":None, "letterIndex":{'I': (0, 0)}},
    45:{"name":"45.dic", "handle":None, "letterIndex":{'p': (0, 0)}},
    5:{"name":"5.dic", "handle":None, "letterIndex":{'!': (0, 9), '1': (21, 83), '0': (9, 21), '5': (97, 119), '4': (83, 97), '7': (119, 133), '9': (143, 163), '8': (133, 143), 'A': (163, 3067), 'C': (5267, 7319), 'B': (3067, 5267), 'E': (8842, 9899), 'D': (7319, 8842), 'G': (10764, 11908), 'F': (9899, 10764), 'I': (13083, 13886), 'H': (11908, 13083), 'K': (14631, 15997), 'J': (13886, 14631), 'M': (17537, 19684), 'L': (15997, 17537), 'O': (20647, 21273), 'N': (19684, 20647), 'Q': (22977, 23086), 'P': (21273, 22977), 'S': (23971, 26604), 'R': (23086, 23971), 'U': (28174, 28664), 'T': (26604, 28174), 'W': (29188, 29966), 'V': (28664, 29188), 'Y': (30092, 30483), 'X': (29966, 30092), 'Z': (30483, 30753), 'a': (30753, 58286), 'c': (88286, 109054), 'b': (58286, 88286), 'e': (129277, 137794), 'd': (109054, 129277), 'g': (148958, 166438), 'f': (137794, 148958), 'i': (179054, 189717), 'h': (166438, 179054), 'k': (198597, 219823), 'j': (189717, 198597), 'm': (239458, 265936), 'l': (219823, 239458), 'o': (280099, 290601), 'n': (265936, 280099), 'q': (312361, 313861), 'p': (290601, 312361), 's': (331704, 369865), 'r': (313861, 331704), 'u': (394607, 402880), 't': (369865, 394607), 'w': (411478, 420527), 'v': (402880, 411478), 'y': (421190, 425833), 'x': (420527, 421190), 'z': (425833, 429413)}},
    53:{"name":"53.dic", "handle":None, "letterIndex":{'I': (0, 0)}},
    6:{"name":"6.dic", "handle":None, "letterIndex":{'!': (0, 10), "'": (10, 25), '1': (85, 375), '0': (25, 85), '3': (466, 479), '2': (375, 466), '5': (533, 559), '4': (479, 533), '7': (592, 631), '6': (559, 592), '9': (642, 668), '8': (631, 642), 'A': (679, 5850), '@': (668, 679), 'C': (9649, 13390), 'B': (5850, 9649), 'E': (15473, 17028), 'D': (13390, 15473), 'G': (18334, 20582), 'F': (17028, 18334), 'I': (22822, 23863), 'H': (20582, 22822), 'K': (24983, 26847), 'J': (23863, 24983), 'M': (29219, 32783), 'L': (26847, 29219), 'O': (34232, 35422), 'N': (32783, 34232), 'Q': (38154, 38315), 'P': (35422, 38154), 'S': (39925, 44715), 'R': (38315, 39925), 'U': (47795, 48184), 'T': (44715, 47795), 'W': (48998, 50032), 'V': (48184, 48998), 'Y': (50104, 50608), 'X': (50032, 50104), 'Z': (50608, 51051), 'a': (51051, 96864), 'c': (157785, 204100), 'b': (96864, 157785), 'e': (239806, 257218), 'd': (204100, 239806), 'g': (277122, 307757), 'f': (257218, 277122), 'i': (330893, 346772), 'h': (307757, 330893), 'k': (360914, 404651), 'j': (346772, 360914), 'm': (439368, 494463), 'l': (404651, 439368), 'o': (516288, 533229), 'n': (494463, 516288), 'q': (576988, 579910), 'p': (533229, 576988), 's': (614938, 687941), 'r': (579910, 614938), 'u': (731514, 749606), 't': (687941, 731514), 'w': (766065, 781813), 'v': (749606, 766065), 'y': (782927, 789014), 'x': (781813, 782927), 'z': (789014, 794972)}},
    7:{"name":"7.dic", "handle":None, "letterIndex":{'!': (0, 11), '1': (25, 51), '0': (11, 25), '5': (63, 77), '4': (51, 63), '7': (77, 91), '8': (91, 103), 'A': (103, 6792), 'C': (11644, 17721), 'B': (6792, 11644), 'E': (19946, 21845), 'D': (17721, 19946), 'G': (23521, 26367), 'F': (21845, 23521), 'I': (28817, 30206), 'H': (26367, 28817), 'K': (31433, 33447), 'J': (30206, 31433), 'M': (36395, 41284), 'L': (33447, 36395), 'O': (42840, 44402), 'N': (41284, 42840), 'Q': (48707, 48931), 'P': (44402, 48707), 'S': (51154, 57264), 'R': (48931, 51154), 'U': (60978, 61458), 'T': (57264, 60978), 'W': (62419, 64123), 'V': (61458, 62419), 'Y': (64299, 64728), 'X': (64123, 64299), 'Z': (64728, 65573), 'a': (65573, 123573), 'c': (207606, 282648), 'b': (123573, 207606), 'e': (331747, 358319), 'd': (282648, 331747), 'g': (387922, 429573), 'f': (358319, 387922), 'i': (462293, 481279), 'h': (429573, 462293), 'k': (498679, 550438), 'j': (481279, 498679), 'm': (592962, 666402), 'l': (550438, 592962), 'o': (696403, 721514), 'n': (666402, 696403), 'q': (791614, 795816), 'p': (721514, 791614), 's': (843845, 947831), 'r': (795816, 843845), 'u': (1005249, 1030104), 't': (947831, 1005249), 'w': (1051822, 1074689), 'v': (1030104, 1051822), 'y': (1075849, 1081930), 'x': (1074689, 1075849), 'z': (1081930, 1089893)}},
    8:{"name":"8.dic", "handle":None, "letterIndex":{'!': (0, 12), '1': (24, 78), '0': (12, 24), '2': (78, 104), '9': (134, 147), '8': (104, 134), 'A': (147, 6997), 'C': (11292, 18453), 'B': (6997, 11292), 'E': (21190, 23740), 'D': (18453, 21190), 'G': (25383, 28559), 'F': (23740, 25383), 'I': (31585, 32837), 'H': (28559, 31585), 'K': (34041, 35707), 'J': (32837, 34041), 'M': (38665, 44051), 'L': (35707, 38665), 'O': (45734, 47247), 'N': (44051, 45734), 'Q': (52750, 53107), 'P': (47247, 52750), 'S': (55042, 61538), 'R': (53107, 55042), 'U': (65904, 66465), 'T': (61538, 65904), 'W': (67516, 68547), 'V': (66465, 67516), 'Y': (68717, 69176), 'X': (68547, 68717), 'Z': (69176, 69635), 'a': (69635, 135870), 'c': (227604, 323383), 'b': (135870, 227604), 'e': (380576, 416575), 'd': (323383, 380576), 'g': (457321, 501588), 'f': (416575, 457321), 'i': (542121, 566689), 'h': (501588, 542121), 'k': (581047, 633058), 'j': (566689, 581047), 'm': (677149, 761935), 'l': (633058, 677149), 'o': (795002, 829126), 'n': (761935, 795002), 'q': (917831, 922908), 'p': (829126, 917831), 's': (979341, 1106800), 'r': (922908, 979341), 'u': (1170360, 1208137), 't': (1106800, 1170360), 'w': (1234399, 1260251), 'v': (1208137, 1234399), 'y': (1261422, 1267351), 'x': (1260251, 1261422), 'z': (1267351, 1274469)}},
    9:{"name":"9.dic", "handle":None, "letterIndex":{'1': (0, 64), '7': (64, 96), '9': (96, 128), 'A': (128, 7130), 'C': (11270, 18649), 'B': (7130, 11270), 'E': (21583, 24301), 'D': (18649, 21583), 'G': (25795, 28801), 'F': (24301, 25795), 'I': (32635, 33733), 'H': (28801, 32635), 'K': (34957, 36055), 'J': (33733, 34957), 'M': (38989, 44893), 'L': (36055, 38989), 'O': (47179, 48871), 'N': (44893, 47179), 'Q': (54451, 54703), 'P': (48871, 54451), 'S': (56395, 63163), 'R': (54703, 56395), 'U': (67393, 67933), 'T': (63163, 67393), 'W': (68941, 69948), 'V': (67933, 68941), 'Y': (70218, 70452), 'X': (69948, 70218), 'Z': (70452, 71136), 'a': (71136, 139145), 'c': (219085, 317205), 'b': (139145, 219085), 'e': (374518, 414561), 'd': (317205, 374518), 'g': (451169, 491727), 'f': (414561, 451169), 'i': (533465, 563356), 'h': (491727, 533465), 'k': (574959, 616786), 'j': (563356, 574959), 'm': (652398, 733674), 'l': (616786, 652398), 'o': (765777, 802029), 'n': (733674, 765777), 'q': (898648, 903919), 'p': (802029, 898648), 's': (957655, 1081453), 'r': (903919, 957655), 'u': (1141768, 1188928), 't': (1081453, 1141768), 'w': (1212988, 1236675), 'v': (1188928, 1212988), 'y': (1237860, 1242332), 'x': (1236675, 1237860), 'z': (1242332, 1249073)}},
}

def convertFiles():
    """Takes wordlists, copies, calculates and appends frequency, concatenates
    and splits based on length, then sorts by first character."""
    lines = 0
    maxLength = 0
    tempFiles = []
    for fn in wordsOrder:
        fIn = open(os.path.join(workPath, fn), "r")

        # Save for deletion later
        fnOut = os.path.join(wordPath, fn)
        tempFiles.append(fnOut)
        fOut = open(fnOut, "w")
        for line in fIn:
            lines += 1
            length = len(line.rstrip("\n\r"))
            if length > maxLength:
                maxLength = length
            fOut.write("{}\t{}\n".format(line.rstrip("\n\r"), lines))
        fIn.close()
        fOut.close()

    # Create new files: "len1, len2", etc (no zero padding)
    lenFiles = {}
    for i in range(1, maxLength + 1):
        lenFiles[i] = open(
            os.path.join(wordPath, str(i) + ".dic"), "w")

    for fn in wordsOrder:
        fIn = open(os.path.join(wordPath, fn), "r")
        for line in fIn:
            length = len(line.split("\t")[0])
            lenFiles[length].write(line)
        fIn.close()

    for fn in lenFiles.values():
        fn.close()

    # Sort and remove duplicates. Slow, but only runs once on wordlist changes
    for fn in lenFiles:
        f = open(os.path.join(wordPath, str(fn) + ".dic"), "r")

        # Remove duplicates and keep the lower line numbers
        lines = {}
        for line in f:
            base, count = line.rstrip("\n\r").split("\t")
            count = int(count)
            if base in lines and lines[base] < count:
                continue
#                lines[base] = count
#                lines[line] = line
            else:
                lines[base] = count
        f.close()
        lines = sorted(["{}\t{}\n".format(k, v) for k, v in lines.iteritems()])
        f = open(os.path.join(wordPath, str(fn) + ".dic"), "w")
        for line in lines:
            f.write(line)
        f.close()

    for fn in tempFiles:
        os.remove(fn)

def indexFiles():
    for fn in os.listdir(wordPath):
        maxLength = 0
        if not fn.endswith(".dic"):
            continue
        size = int(os.stat(os.path.join(wordPath, fn)).st_size)
        f = open(os.path.join(wordPath, fn), "r")
        if not size:
            continue
        contents = mmap.mmap(f.fileno(), size, access=mmap.ACCESS_READ)
        f.close()

        # Letter indexing
        letterIndex = {}
        stack = []
        lastPos = 0

#        for letter in sorted(string.printable):
#            start = None
#
#            # Get around Python file iteration not playing well with .tell()
#            while True:
#                pos = contents.tell()
#                line = contents.readline()
#                if not line:
#                    break
#                if line[0] == letter:
#                    start = pos
#                    break
#            contents.seek(0)

        letterIndex = {}
        for letter in sorted(string.printable):
            result = re.search(r"^{}".format(re.escape(letter)), contents, re.M)
            if result:
                start = result.start()
                while len(stack) > 0:
                    stack.pop().append(start)
                letterIndex[letter] = [start,]
                stack.append(letterIndex[letter])
                lastPos = start
            #else:
                #letterIndex[letter] = None
                #stack.append(letterIndex[letter])
        while len(stack) > 0:
            element = stack.pop()
            if element[0]:
                element.append(size)
            else:
                element.append(0)

        # Max length (no longer needed)
#        for line in iter(contents.readline, ""):
#            line = line.rstrip("\r\n")
#            if len(line.rstrip()) > maxLength:
#                maxLength = len(line)

        # Character set (no longer needed)
#        type = getType(contents)

        # Line count (no longer needed)
#        lines = 0
#        contents.seek(0)
#        while contents.readline():
#            lines += 1

        letterIndex = {k: tuple(v) for k, v in letterIndex.items()}
        print '{}:{{"name":"{}", "handle":None, "letterIndex":{}}},'.format(
            fn.split(".")[0], fn, letterIndex)

#def getType(item):
#    if re.search(r"[^a-zA-Z0-9'\n\r]", item):
#        return 3
#    if re.search(r"[^a-z'\n\r]", item):
#        return 2
#    elif not re.search(r"[^0-9\n\r]", item):
#        return 1
#    return 0

def openFiles():
    for fn in wordFiles.values():
        fn["handle"] = open(os.path.join("words", fn["name"]), "r")

def closeFiles():
    for fn in wordFiles:
        fn["handle"].close()

def findWord(word):
    # Open files if necessary
    if len(word) not in wordFiles:
        return False
    if wordFiles[1]["handle"] is None:
        openFiles()
    fn = wordFiles[len(word)]

    # Get the ASCII letter or character after the first
    first = word[0]
    if first not in fn["letterIndex"]:
        return False
    length = len(word)
    # Cheap(er) ways of skipping file searches
    # TODO: Index character set of file instead of using basic type

    #print "Searching file: {} for term: {}".format(fn["name"], word)
    location = binary_search.searchFile(
        fn["handle"],
        word,
        fn["letterIndex"][first][0],
        fn["letterIndex"][first][1],
        splitChar="\t")
    if location:
        #print "Word {} found after {} searches".format(word, location)
        return location
    return False

if __name__ == "__main__":
    #cProfile.run("findWord('illinois')")
    convertFiles()
    indexFiles()
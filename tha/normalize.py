# Copyright (c) 2021-2022, SIL International.
# Licensed under MIT license: https://opensource.org/licenses/MIT
import enum
import re
from ftfy import fix_text, TextFixerConfig


class Cats(enum.Enum):
  Other = 0
  Base = 1
  Robat = 2
  Coeng = 3
  ZFCoeng = 4
  Shift = 5
  Z = 6
  VPre = 7
  VB = 8
  VA = 9
  VPost = 10
  MS = 11
  MF = 12


categories = (
  [Cats.Base] * 35  # 1780-17A2
  + [Cats.Other] * 2  # 17A3-17A4
  + [Cats.Base] * 15  # 17A5-17B3
  + [Cats.Other] * 2  # 17B4-17B5
  + [Cats.VPost]  # 17B6
  + [Cats.VA] * 4  # 17B7-17BA
  + [Cats.VB] * 3  # 17BB-17BD
  + [Cats.VPre] * 8  # 17BE-17C5
  + [Cats.MS]  # 17C6
  + [Cats.MF] * 2  # 17C7-17C8
  + [Cats.Shift] * 2  # 17C9-17CA
  + [Cats.MS]  # 17CB
  + [Cats.Robat]  # 17CC
  + [Cats.MS] * 5  # 17CD-17D1
  + [Cats.Coeng]  # 17D2
  + [Cats.MS]  # 17D3
  + [Cats.Other] * 9  # 17D4-17DC
  + [Cats.MS]
)  # 17DD

khres = {  # useful regular sub expressions used later
  "B": "[\u1780-\u17a2\u17a5-\u17b3\u25cc]",
  "NonRo": "[\u1780-\u1799\u179b-\u17a2\u17a5-\u17b3]",
  "NonBA": "[\u1780-\u1793\u1795-\u17a2\u17a5-\u17b3]",
  "S1": "[\u1780-\u1783\u1785-\u1788\u178a-\u178d\u178f-\u1792"
  "\u1795-\u1797\u179e-\u17a0\u17a2]",
  "S2": "[\u1784\u1780\u178e\u1793\u1794\u1798-\u179d\u17a1\u17a3-\u17b3]",
  "VAA": "(?:[\u17b7-\u17ba\u17be\u17bf\u17dd]|\u17b6\u17c6)",
  "VA": "(?:[\u17c1-\u17c5]?{VAA})",
  "VAS": "(?:{VA}|[\u17c1-\u17c3]?\u17d0)",
  "VB": "(?:[\u17c1-\u17c3][\u17bb-\u17bd])",
  # contains series 1 and no BA
  "STRONG": "{S1}\u17cc?(?:\u17d2{NonBA}(?:\u17d2{NonBA})?)?|"
  "{NonBA}\u17cc?(?:\u17d2{S1}(?:\u17d2{NonBA})?|\u17d2{NonBA}\u17d2{S1})",
  # contains BA or only series 2
  "NSTRONG": "(?:{S2}\u17cc?(?:\u17d2{S2}(?:\u17d2{S2})?)?|\u1794\u17cc?{COENG}?|"
  "{B}\u17cc?(?:\u17d2{NonRo}\u17d2\u1794|\u17d2\u1794(?:\u17d2{B}))?)",
  "COENG": "(?:(?:\u17d2{NonRo})?\u17d2{B})",
  # final right spacing coeng
  "COENGR": "(?:(?:[\u17c9\u17ca]\u200c?)?(?:{VB}?{VAS}|{VB}))",
  # final all coengs
  "COENGF": "(?:(?:[\u17c9\u17ca]\u200c?)?[\u17c2-\u17c3]?{VB}?{VA}?"
  "[\u17b6\u17bf\u17c0\u17c4\u17c5])",
  "COENGS": "(?:\u17c9\u200c?{VAS})",
  "FCOENG": "(?:\u17d2\u200d{NonRo})",
  "SHIFT": "(?:(?<={STRONG}{FCOENG}?)\u17ca\u200c(?={VA})|"
  "(?<={NSTRONG}{FCOENG}?)\u17c9\u200c(?={VAS})|[\u17c9\u17ca])",
  "V": "(?:\u17c1[\u17bc\u17bd]?[\u17b7\u17b9\u17ba]?|"
  "[\u17c2\u17c3]?[\u17bc\u17bd]?[\u17b7-\u17ba]\u17b6|"
  "[\u17c2\u17c3]?[\u17bb-\u17bd]?\u17b6|\u17be[\u17bc\u17bd]?\u17b6?|"
  "[\u17c1-\u17c5]?\u17bb(?![\u17d0\u17dd])|"
  "[\u17bf\u17c0]|[\u17c2-\u17c5]?[\u17bc\u17bd]?[\u17b7-\u17ba]?)",
  "MS": "(?:(?:[\u17c6\u17cb\u17cd-\u17cf\u17d1\u17d3]|"
  "(?<!\u17bb[\u17b6\u17c4\u17c5]?)[\u17d0\u17dd])"
  "[\u17c6\u17cb\u17cd-\u17d1\u17d3\u17dd]?)",
}

# expand 2 times: CEONGS -> VAS -> VA -> VAA
for i in range(3):
  khres = {k: v.format(**khres) for k, v in khres.items()}


def charcat(c):
  """Returns the Khmer character category for a single char string"""
  o = ord(c)
  if 0x1780 <= o <= 0x17DD:
    return categories[o - 0x1780]
  elif o == 0x200C:
    return Cats.Z
  elif o == 0x200D:
    return Cats.ZFCoeng
  return Cats.Other


def _reorder(txt, lang="km"):
  """Returns khmer normalised string, without fixing or marking errors"""
  # Mark final coengs in Middle Khmer
  if lang == "xhm":
    txt = re.sub(r"([\u17B7-\u17C5]\u17D2)", "\\1\u200d", txt)
  # Categorise every character in the string
  charcats = [charcat(c) for c in txt]

  # Recategorise base or ZWJ -> coeng after coeng char
  for i in range(1, len(charcats)):
    if charcats[i - 1] == Cats.Coeng and charcats[i] in (Cats.Base, Cats.ZFCoeng):
      charcats[i] = Cats.Coeng

  # Find subranges of base+non other and sort components in the subrange
  i = 0
  res = []
  while i < len(charcats):
    c = charcats[i]
    if c != Cats.Base:
      res.append(txt[i])
      i += 1
      continue
    # Scan for end of syllable
    j = i + 1
    while j < len(charcats) and charcats[j].value > Cats.Base.value:
      j += 1
    # Sort syllable based on character categories
    # Sort the char indices by category then position in string
    newindices = sorted(range(i, j), key=lambda e: (charcats[e].value, e))
    replaces = "".join(txt[n] for n in newindices)

    replaces = re.sub(
      "([\u200c\u200d]\u17d2?|\u17d2\u200d)[\u17d2\u200c\u200d]+", r"\1", replaces
    )  # remove multiple invisible chars
    # map compoound vowel sequences to compounds with -u before to be converted
    replaces = re.sub("\u17c1([\u17bb-\u17bd]?)\u17b8", "\u17be\\1", replaces)
    replaces = re.sub("\u17c1([\u17bb-\u17bd]?)\u17b6", "\u17c4\\1", replaces)
    replaces = re.sub("(\u17be)(\u17bb)", r"\2\1", replaces)
    # Replace -u + upper vowel with consonant shifter
    replaces = re.sub(
      "({STRONG}{FCOENG}?[\u17c1-\u17c5]?)\u17bb" "(?={VAA}|\u17d0)".format(**khres),
      "\\1\u17ca",
      replaces,
    )
    replaces = re.sub(
      "({NSTRONG}{FCOENG}?[\u17c1-\u17c5]?)\u17bb" "(?={VAA}|\u17d0)".format(**khres),
      "\\1\u17c9",
      replaces,
    )
    replaces = re.sub(
      "(\u17d2\u179a)(\u17d2[\u1780-\u17b3])", r"\2\1", replaces
    )  # coeng ro second
    replaces = re.sub("(\u17d2)\u178a", "\\1\u178f", replaces)  # coeng da->ta
    res.append(replaces)
    i = j
  return "".join(res)


CHAR_REPLACEMENTS = str.maketrans(
  {
    "¹": "1",
    "²": "2",
    "³": "3",
    "À": "A",
    "Á": "A",
    "Â": "A",
    "Ã": "A",
    "Ä": "A",
    "Å": "A",
    "Ā": "A",
    "Ă": "A",
    "Ą": "A",
    "Ǎ": "A",
    "Ǟ": "A",
    "Ǡ": "A",
    "Ǻ": "A",
    "Ȁ": "A",
    "Ȃ": "A",
    "Ȧ": "A",
    "Ḁ": "A",
    "Ạ": "A",
    "Ả": "A",
    "Ấ": "A",
    "Ầ": "A",
    "Ẩ": "A",
    "Ẫ": "A",
    "Ậ": "A",
    "Ắ": "A",
    "Ằ": "A",
    "Ẳ": "A",
    "Ẵ": "A",
    "Ặ": "A",
    "à": "a",
    "á": "a",
    "â": "a",
    "ã": "a",
    "ä": "a",
    "å": "a",
    "ª": "a",
    "ā": "a",
    "ă": "a",
    "ą": "a",
    "ǎ": "a",
    "ǟ": "a",
    "ǡ": "a",
    "ǻ": "a",
    "ȁ": "a",
    "ȃ": "a",
    "ȧ": "a",
    "ḁ": "a",
    "ạ": "a",
    "ả": "a",
    "ấ": "a",
    "ầ": "a",
    "ẩ": "a",
    "ẫ": "a",
    "ậ": "a",
    "ắ": "a",
    "ằ": "a",
    "ẳ": "a",
    "ẵ": "a",
    "ặ": "a",
    "Ḃ": "B",
    "Ḅ": "B",
    "Ḇ": "B",
    "ḃ": "b",
    "ḅ": "b",
    "ḇ": "b",
    "Ç": "C",
    "Ć": "C",
    "Ĉ": "C",
    "Ċ": "C",
    "Č": "C",
    "Ḉ": "C",
    "ç": "c",
    "ć": "c",
    "ĉ": "c",
    "ċ": "c",
    "č": "c",
    "ḉ": "c",
    "Ð": "D",
    "Ď": "D",
    "Đ": "D",
    "Ḋ": "D",
    "Ḍ": "D",
    "Ḏ": "D",
    "Ḑ": "D",
    "Ḓ": "D",
    "ď": "d",
    "đ": "d",
    "ḋ": "d",
    "ḍ": "d",
    "ḏ": "d",
    "ḑ": "d",
    "ḓ": "d",
    "È": "E",
    "É": "E",
    "Ê": "E",
    "Ë": "E",
    "Ē": "E",
    "Ĕ": "E",
    "Ė": "E",
    "Ę": "E",
    "Ě": "E",
    "Ȅ": "E",
    "Ȇ": "E",
    "Ȩ": "E",
    "Ḕ": "E",
    "Ḗ": "E",
    "Ḙ": "E",
    "Ḛ": "E",
    "Ḝ": "E",
    "Ẹ": "E",
    "Ẻ": "E",
    "Ẽ": "E",
    "Ế": "E",
    "Ề": "E",
    "Ể": "E",
    "Ễ": "E",
    "Ệ": "E",
    "è": "e",
    "é": "e",
    "ê": "e",
    "ë": "e",
    "ē": "e",
    "ĕ": "e",
    "ė": "e",
    "ę": "e",
    "ě": "e",
    "ȅ": "e",
    "ȇ": "e",
    "ȩ": "e",
    "ḕ": "e",
    "ḗ": "e",
    "ḙ": "e",
    "ḛ": "e",
    "ḝ": "e",
    "ẹ": "e",
    "ẻ": "e",
    "ẽ": "e",
    "ế": "e",
    "ề": "e",
    "ể": "e",
    "ễ": "e",
    "ệ": "e",
    "Ḟ": "F",
    "ḟ": "f",
    "Ĝ": "G",
    "Ğ": "G",
    "Ġ": "G",
    "Ģ": "G",
    "Ǧ": "G",
    "Ǵ": "G",
    "Ḡ": "G",
    "ĝ": "g",
    "ğ": "g",
    "ġ": "g",
    "ģ": "g",
    "ǧ": "g",
    "ǵ": "g",
    "ḡ": "g",
    "Ĥ": "H",
    "Ħ": "H",
    "Ȟ": "H",
    "Ḣ": "H",
    "Ḥ": "H",
    "Ḧ": "H",
    "Ḩ": "H",
    "Ḫ": "H",
    "ĥ": "h",
    "ħ": "h",
    "ȟ": "h",
    "ḣ": "h",
    "ḥ": "h",
    "ḧ": "h",
    "ḩ": "h",
    "ḫ": "h",
    "ẖ": "h",
    "Ì": "I",
    "Í": "I",
    "Î": "I",
    "Ï": "I",
    "Ĩ": "I",
    "Ī": "I",
    "Ĭ": "I",
    "Į": "I",
    "İ": "I",
    "Ǐ": "I",
    "Ȉ": "I",
    "Ȋ": "I",
    "Ḭ": "I",
    "Ḯ": "I",
    "Ỉ": "I",
    "Ị": "I",
    "ì": "i",
    "í": "i",
    "î": "i",
    "ï": "i",
    "ĩ": "i",
    "ī": "i",
    "ĭ": "i",
    "į": "i",
    "ı": "i",
    "ǐ": "i",
    "ȉ": "i",
    "ȋ": "i",
    "ḭ": "i",
    "ḯ": "i",
    "ỉ": "i",
    "ị": "i",
    "Ĵ": "J",
    "ĵ": "j",
    "Ķ": "K",
    "Ǩ": "K",
    "Ḱ": "K",
    "Ḳ": "K",
    "Ḵ": "K",
    "ķ": "k",
    "ǩ": "k",
    "ḱ": "k",
    "ḳ": "k",
    "ḵ": "k",
    "Ĺ": "L",
    "Ļ": "L",
    "Ľ": "L",
    "Ŀ": "L",
    "Ł": "L",
    "Ḷ": "L",
    "Ḹ": "L",
    "Ḻ": "L",
    "Ḽ": "L",
    "ĺ": "l",
    "ļ": "l",
    "ľ": "l",
    "ŀ": "l",
    "ł": "l",
    "ḷ": "l",
    "ḹ": "l",
    "ḻ": "l",
    "ḽ": "l",
    "Ḿ": "M",
    "Ṁ": "M",
    "Ṃ": "M",
    "ḿ": "m",
    "ṁ": "m",
    "ṃ": "m",
    "Ñ": "N",
    "Ń": "N",
    "Ņ": "N",
    "Ň": "N",
    "Ǹ": "N",
    "Ṅ": "N",
    "Ṇ": "N",
    "Ṉ": "N",
    "Ṋ": "N",
    "ñ": "n",
    "ń": "n",
    "ņ": "n",
    "ň": "n",
    "ǹ": "n",
    "ṅ": "n",
    "ṇ": "n",
    "ṉ": "n",
    "ṋ": "n",
    "Ò": "O",
    "Ó": "O",
    "Ô": "O",
    "Õ": "O",
    "Ö": "O",
    "Ō": "O",
    "Ŏ": "O",
    "Ő": "O",
    "Ơ": "O",
    "Ǒ": "O",
    "Ǫ": "O",
    "Ǭ": "O",
    "Ȍ": "O",
    "Ȏ": "O",
    "Ȫ": "O",
    "Ȭ": "O",
    "Ȯ": "O",
    "Ȱ": "O",
    "Ṍ": "O",
    "Ṏ": "O",
    "Ṑ": "O",
    "Ṓ": "O",
    "Ọ": "O",
    "Ỏ": "O",
    "Ố": "O",
    "Ồ": "O",
    "Ổ": "O",
    "Ỗ": "O",
    "Ộ": "O",
    "Ớ": "O",
    "Ờ": "O",
    "Ở": "O",
    "Ỡ": "O",
    "Ợ": "O",
    "ò": "o",
    "ó": "o",
    "ô": "o",
    "õ": "o",
    "ö": "o",
    "ō": "o",
    "ŏ": "o",
    "ő": "o",
    "ơ": "o",
    "ǒ": "o",
    "ǫ": "o",
    "ǭ": "o",
    "ȍ": "o",
    "ȏ": "o",
    "ȫ": "o",
    "ȭ": "o",
    "ȯ": "o",
    "ȱ": "o",
    "ṍ": "o",
    "ṏ": "o",
    "ṑ": "o",
    "ṓ": "o",
    "ọ": "o",
    "ỏ": "o",
    "ố": "o",
    "ồ": "o",
    "ổ": "o",
    "ỗ": "o",
    "ộ": "o",
    "ớ": "o",
    "ờ": "o",
    "ở": "o",
    "ỡ": "o",
    "ợ": "o",
    "Ṕ": "P",
    "Ṗ": "P",
    "ṕ": "p",
    "ṗ": "p",
    "Ŕ": "R",
    "Ŗ": "R",
    "Ř": "R",
    "Ȑ": "R",
    "Ȓ": "R",
    "Ṙ": "R",
    "Ṛ": "R",
    "Ṝ": "R",
    "Ṟ": "R",
    "ŕ": "r",
    "ŗ": "r",
    "ř": "r",
    "ȑ": "r",
    "ȓ": "r",
    "ṙ": "r",
    "ṛ": "r",
    "ṝ": "r",
    "ṟ": "r",
    "Ś": "S",
    "Ŝ": "S",
    "Ş": "S",
    "Š": "s",
    "Ș": "S",
    "Ṡ": "S",
    "Ṣ": "S",
    "Ṥ": "S",
    "Ṧ": "S",
    "Ṩ": "S",
    "ś": "s",
    "ŝ": "s",
    "ş": "s",
    "š": "s",
    "ș": "s",
    "ṡ": "s",
    "ṣ": "s",
    "ṥ": "s",
    "ṧ": "s",
    "ṩ": "s",
    "Ţ": "T",
    "Ť": "T",
    "Ŧ": "T",
    "Ț": "T",
    "Ṫ": "T",
    "Ṭ": "T",
    "Ṯ": "T",
    "Ṱ": "T",
    "ţ": "t",
    "ť": "t",
    "ŧ": "t",
    "ț": "t",
    "ṫ": "t",
    "ṭ": "t",
    "ṯ": "t",
    "ṱ": "t",
    "ẗ": "t",
    "Ù": "U",
    "Ú": "U",
    "Û": "U",
    "Ü": "U",
    "Ũ": "U",
    "Ū": "U",
    "Ŭ": "U",
    "Ů": "U",
    "Ű": "U",
    "Ų": "U",
    "Ư": "U",
    "Ǔ": "U",
    "Ǖ": "U",
    "Ǘ": "U",
    "Ǚ": "U",
    "Ǜ": "U",
    "Ȕ": "U",
    "Ȗ": "U",
    "Ṳ": "U",
    "Ṵ": "U",
    "Ṷ": "U",
    "Ṹ": "U",
    "Ṻ": "U",
    "Ụ": "U",
    "Ủ": "U",
    "Ứ": "U",
    "Ừ": "U",
    "Ử": "U",
    "Ữ": "U",
    "Ự": "U",
    "ù": "u",
    "ú": "u",
    "û": "u",
    "ü": "u",
    "ũ": "u",
    "ū": "u",
    "ŭ": "u",
    "ů": "u",
    "ű": "u",
    "ų": "u",
    "ư": "u",
    "ǔ": "u",
    "ǖ": "u",
    "ǘ": "u",
    "ǚ": "u",
    "ǜ": "u",
    "ȕ": "u",
    "ȗ": "u",
    "ṳ": "u",
    "ṵ": "u",
    "ṷ": "u",
    "ṹ": "u",
    "ṻ": "u",
    "ụ": "u",
    "ủ": "u",
    "ứ": "u",
    "ừ": "u",
    "ử": "u",
    "ữ": "u",
    "ự": "u",
    "Ṽ": "V",
    "Ṿ": "V",
    "ṽ": "v",
    "ṿ": "v",
    "Ŵ": "W",
    "Ẁ": "W",
    "Ẃ": "W",
    "Ẅ": "W",
    "Ẇ": "W",
    "Ẉ": "W",
    "ŵ": "w",
    "ẁ": "w",
    "ẃ": "w",
    "ẅ": "w",
    "ẇ": "w",
    "ẉ": "w",
    "ẘ": "w",
    "Ẋ": "X",
    "Ẍ": "X",
    "ẋ": "x",
    "ẍ": "x",
    "Ý": "y",
    "Ŷ": "Y",
    "Ÿ": "Y",
    "Ȳ": "Y",
    "Ẏ": "Y",
    "Ỳ": "Y",
    "Ỵ": "Y",
    "Ỷ": "Y",
    "Ỹ": "Y",
    "ý": "y",
    "ÿ": "y",
    "ŷ": "y",
    "ȳ": "y",
    "ẏ": "y",
    "ỳ": "y",
    "ỵ": "y",
    "ỷ": "y",
    "ỹ": "y",
    "ẙ": "y",
    "Ź": "Z",
    "Ż": "Z",
    "Ž": "Z",
    "Ẑ": "Z",
    "Ẓ": "Z",
    "Ẕ": "Z",
    "ź": "z",
    "ż": "z",
    "ž": "z",
    "ẑ": "z",
    "ẓ": "z",
    "ẕ": "z",
    "Ĳ": "IJ",
    "ĳ": "ij",
    "ø": "o",
    "Ø": "O",
    "ɨ": "i",
    "ð": "d",
  }
)


UNICODE_REPLACEMENTS = {
  "\u00ad": "",
  "\u09af\u09bc": "\u09df",
  "\u09a2\u09bc": "\u09dd",
  "\u09a1\u09bc": "\u09dc",
  "\u09ac\u09bc": "\u09b0",
  "\u09c7\u09be": "\u09cb",
  "\u09c7\u09d7": "\u09cc",
  "\u0985\u09be": "\u0986",
  "\u09c7\u0981\u09d7": "\u09cc\u0981",
  "\u09c7\u0981\u09be": "\u09cb\u0981",
  "\u09c7([^\u09d7])\u09d7": "\\g<1>\u09cc",
  "\u00a0": " ",
  "\u200b": "",
  "\u2060": "",
  "\u201e": '"',
  "\u201c": '"',
  "\u201d": '"',
  "\u2013": "-",
  "\u2014": " - ",
  "\u00b4": "'",
  "\u2018": "'",
  "\u201a": "'",
  "\u2019": "'",
  "\u00b4\u00b4": '"',
  # "\u2026": "...",
  "\u00a0\u00ab\u00a0": '"',
  "\u00ab\u00a0": '"',
  "\u00ab": '"',
  "\u00a0\u00bb\u00a0": '"',
  "\u00a0\u00bb": '"',
  "\u00bb": '"',
  "\u09f7": "\u0964",
  "\uff0c": ",",
  "\u3001": ",",
  "\u2236": ":",
  "\uff1a": ":",
  "\uff1f": "?",
  "\u300a": '"',
  "\u300b": '"',
  "\uff09": ")",
  "\uff01": "!",
  "\uff08": "(",
  "\uff1b": ";",
  "\u300d": '"',
  "\u300c": '"',
  "\uff10": "0",
  "\uff11": "1",
  "\uff12": "2",
  "\uff13": "3",
  "\uff14": "4",
  "\uff15": "5",
  "\uff16": "6",
  "\uff17": "7",
  "\uff18": "8",
  "\uff19": "9",
  "\uff5e": "~",
  "\u2501": "-",
  "\u3008": "<",
  "\u3009": ">",
  "\u3010": "[",
  "\u3011": "]",
  "\uff05": "%",
  # Khmer chars
  "។ល។": "\u17d8",
  "ឨញ្ញា": "ឧក",
  "ឣ": "អ",
  "ឤ": "អា",
  "ឲ": "ឱ",
  "\u17dd": "\u17d1",
  "\u17d3": "\u17c6",
  "\u17c1\u17b8": "\u17be",
  "\u17b8\u17c1": "\u17be",
  "\u17c1\u17b6": "\u17c4",
  "\u17bb\u17d0": "\u17c9\u17d0",
  "\u17c9\u17c6": "\u17bb\u17c6",
  "\u17c6\u17bb": "\u17bb\u17c6",
  "\u17c7\u17b7": "\u17b7\u17c7",
  "\u17c7\u17b9": "\u17b9\u17c7",
  "\u17c7\u17ba": "\u17ba\u17c7",
  "\u17c7\u17c2": "\u17c2\u17c7",
  "\u17c6\u17b6": "\u17b6\u17c6",
  "\u17c7\u17bb": "\u17bb\u17c7",
  "\u17c7\u17c1": "\u17c1\u17c7",
  "\u17c7\u17c4": "\u17c4\u17c7",
  "\u17c6\u17bb": "\u17bb\u17c6",
  # common misspelled words
  "រយះពេល": "រយៈពេល",
  "រយ:": "រយៈ",
  "រយះកាល": "រយៈកាល",
  "រយ:កាល": "រយៈកាល",
  "មួយរយះ": "មួយរយៈ",
  "មួយរយ:": "មួយរយៈ",
}

UNICODE_REPLACEMENTS_REGEX = re.compile("|".join(UNICODE_REPLACEMENTS.keys()))

DOUBLE_QUOTE_REGEX = re.compile(
  "|".join(
    [
      "«",
      "‹",
      "»",
      "›",
      "„",
      "“",
      "‟",
      "”",
      "❝",
      "❞",
      "❮",
      "❯",
      "〝",
      "〞",
      "〟",
      "＂",
    ]
  )
)

SINGLE_QUOTE_REGEX = re.compile("|".join(["‘", "‛", "’", "❛", "❜", "`", "´", "‘", "’"]))
WHITESPACES_HANDLER_REGEX = re.compile(r"[^\S\r\n]+")
MULTIPLE_PUNCT_REGEX = re.compile(r"([៙៚៖!?។៕\u17d8])\1+")


def clean_khmer_trailing_vowels(text):
  text = re.sub(r"([\u17b6-\u17dd])\1+", r"\1", text)
  return text


def processor(text: str):
  # remove zero width spaces
  text = text.replace("\u200b", "").replace("\u200a", "").strip()
  # censored dots for sensitive words
  text = re.sub(r"([\u1780-\u17dd]{2,})([\,\.]+)([\u1780-\u17dd])", r"\1\3", text)
  # fix unicode text
  text = fix_text(text, config=TextFixerConfig(normalization="NFKC", explain=False))
  # qoutes string
  text = SINGLE_QUOTE_REGEX.sub("'", text)
  text = DOUBLE_QUOTE_REGEX.sub('"', text)
  # repeating punctuations
  text = MULTIPLE_PUNCT_REGEX.sub(r"\1", text)
  # trailing/invalid vowels
  text = clean_khmer_trailing_vowels(text)
  # replace accents
  text = text.translate(CHAR_REPLACEMENTS)
  # replace unicode variations
  text = UNICODE_REPLACEMENTS_REGEX.sub(
    lambda match: UNICODE_REPLACEMENTS.get(match.group(0), f"{match.group(1)}\u09cc"),
    text,
  )

  # normalize white spaces
  text = WHITESPACES_HANDLER_REGEX.sub(" ", text)
  # ellipsis
  text = re.sub(r"\.{3,}", "\u2026", text)

  # add space between punctuations, so tokenizer can separate it well.
  text = re.sub(r"\s*([៙៚៖!?។៕\u17d8])", r" \1", text)

  # remove repeating repeater
  text = re.sub(r"[^\S\r\n]+ៗ", "ៗ", text)

  return text

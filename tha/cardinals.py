import regex as re
import math

DEFAULT_MINUS = "ដក"
DEFAULT_DELIMITER = "ក្បៀស"
DEFAULT_SEPARATOR = "▁"

digits = [
  "សូន្យ",
  "មួយ",
  "ពីរ",
  "បី",
  "បួន",
  "ប្រាំ",
  "ប្រាំមួយ",
  "ប្រាំពីរ",
  "ប្រាំបី",
  "ប្រាំបួន",
]

prefix = [
  "",
  "ដប់",
  "ម្ភៃ",
  "សាមសិប",
  "សែសិប",
  "ហាសិប",
  "ហុកសិប",
  "ចិតសិប",
  "ប៉ែតសិប",
  "កៅសិប",
]

suffix = dict(
  [
    (2, "រយ"),
    (3, "ពាន់"),
    (4, "ម៉ឺន"),
    (5, "សែន"),
    (6, "លាន"),
    (9, "ប៊ីលាន"),
    (12, "ទ្រីលាន"),
    (15, "ក្វាទ្រីលាន"),
    (18, "គ្វីនទីលាន"),
    (21, "សិចទីលាន"),
    (24, "សិបទីលាន"),
    (27, "អុកទីលាន"),
    (30, "ណូនីលាន"),
    (33, "ដេស៊ីលាន"),
    (36, "អាន់ដេស៊ីលាន"),
  ]
)


def cardinal_processor(num, sep=DEFAULT_SEPARATOR, minus_sign=DEFAULT_MINUS):
  if math.isnan(num):
    return ""

  if num < 0:
    return minus_sign + sep + cardinal_processor(abs(num), sep)

  num = math.floor(num)

  if num < 10:
    return digits[num]

  if num < 100:
    r = num % 10
    if r == 0:
      return prefix[num // 10]
    return prefix[num // 10] + cardinal_processor(r, sep)

  exp = math.floor(math.log10(num))

  while exp not in suffix and exp > 0:
    exp = exp - 1

  d = 10**exp
  pre = cardinal_processor(num // d, sep)
  suf = suffix[exp]
  r = num % d

  if r == 0:
    return pre + suf

  return pre + suf + sep + cardinal_processor(r, sep)


RE_CARDINALS = re.compile(r"[\-+]?[\u17e0-\u17e90-9]+")


def processor(text: str, sep=DEFAULT_SEPARATOR, minus_sign=DEFAULT_MINUS) -> str:
  return RE_CARDINALS.sub(
    lambda m: cardinal_processor(int(m[0]), sep=sep, minus_sign=minus_sign), text
  )

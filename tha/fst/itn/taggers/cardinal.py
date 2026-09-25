import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import TH_DIGIT, TH_NON_ZERO, GraphFst, field, load

# "ដកដប់" -> -10: ដក before a number is a minus sign
MINUS = "ដក"

# single digits are only written as digits after these words: "ទីបី" -> "ទី3",
# "លេខប្រាំ" -> "លេខ5", on their own they are usually words ("មួយចំនួន")
PREFIXES = ["ទី", "លេខ"]


def _not_zeros(width: int) -> pynini.Fst:
  return pynini.difference(TH_DIGIT**width, "0" * width).optimize()


class CardinalFst(GraphFst):
  """
  Spoken integers, e.g.
    មួយពាន់ពីររយសាមសិបបួន -> cardinal { integer: "1234" }
    ដប់ពាន់ (colloquial)    -> cardinal { integer: "10,000" }
    សាមប្រាំ (សាមសិបប្រាំ)  -> cardinal { integer: "35" }
    សូន្យសូន្យប្រាំពីរ       -> cardinal { integer: "007" }
    ទីបី                   -> cardinal { prefix: "ទី" integer: "3" }
    ដកដប់                  -> cardinal { negative: "-" integer: "10" }

  The number is built as a zero padded 15 digit string, one block per scale
  word, then the leading zeros are removed.
  """

  def __init__(
    self, grouping: pynini.Fst, single_digits: bool = False, variants: bool = True
  ):
    super().__init__(name="cardinal", kind="classify")

    # plus spellings that follow the pronunciation: ប្រាំពិល (ប្រាំពីរ)
    digit = pynini.invert(load("digit.tsv"))
    if variants:
      digit |= load("digit_variants.tsv")
    zero = pynini.invert(load("zero.tsv"))
    ties = pynini.invert(load("ties.tsv"))
    # "សាមប្រាំ", "ហុកពីរ": the short forms of the tens need a digit after them
    ties_short = load("ties_short.tsv")

    def scale(word):
      return pynutil.delete(word)

    zero_1 = pynutil.insert("0")
    ones = digit | zero_1
    tens = (ties + ones) | (ties_short + digit) | (zero_1 + ones)
    hundreds = (digit + scale("រយ") + tens) | (zero_1 + tens)
    tens_nz = (tens @ _not_zeros(2)).optimize()
    hundreds_nz = (hundreds @ _not_zeros(3)).optimize()

    # below a million: [សែន][ម៉ឺន][ពាន់] hundreds, or the colloquial
    # "ដប់ពាន់" / "មួយរយពាន់" (thousands counted up to 999), "ដប់ម៉ឺន"
    def place(word):
      return (digit + scale(word)) | zero_1

    thousand = place("ពាន់")
    six = pynini.union(
      place("សែន") + place("ម៉ឺន") + thousand + hundreds,
      hundreds_nz + scale("ពាន់") + hundreds,
      tens_nz + scale("ម៉ឺន") + thousand + hundreds,
    ).optimize()
    six_nz = (six @ _not_zeros(6)).optimize()

    # "មួយពាន់លាន" is a billion: millions are counted up to 999,999
    small = (
      pynutil.insert("0" * 3)
      + ((six_nz + scale("លាន")) | pynutil.insert("0" * 6))
      + six
    )
    big = (
      ((hundreds_nz + scale("ទ្រីលាន")) | pynutil.insert("0" * 3))
      + ((hundreds_nz + scale("ប៊ីលាន")) | pynutil.insert("0" * 3))
    ) @ _not_zeros(6)
    big += ((hundreds_nz + scale("លាន")) | pynutil.insert("0" * 3)) + six
    strip = pynutil.delete(pynini.closure("0")) + TH_NON_ZERO + pynini.closure(TH_DIGIT)
    graph_nz = ((small | big) @ strip).optimize()

    # plain digits without grouping, used by the other classes
    self.graph = (graph_nz | zero).optimize()
    self.graph_nz = graph_nz
    # សូន្យប្រាំ -> 05, សូន្យសូន្យ -> 00
    zeros = pynini.closure(zero, 1)
    self.graph_zero_padded = (zeros + (graph_nz | zero)).optimize()
    self.graph_any = (self.graph | self.graph_zero_padded).optimize()
    self.digit = digit
    self.zero = zero

    grouped = (self.graph @ grouping).optimize()
    self.graph_grouped = grouped

    # on their own, only numbers from 10 up (and zero padded ones) are digits
    # (`single_digits` turns this off, to measure what it prevents)
    two_digits = TH_NON_ZERO + pynini.closure(TH_DIGIT, 0 if single_digits else 1)
    plain = ((graph_nz @ two_digits) @ grouping) | self.graph_zero_padded
    prefix = field("prefix", pynini.union(*PREFIXES)) + pynutil.insert(" ")
    # a sign makes a single digit a number too: ដកប្រាំ -> -5
    self.negative = (
      pynutil.delete(MINUS)
      + field("negative", pynutil.insert("-"))
      + (pynutil.insert(" "))
    )
    graph = pynini.union(
      field("integer", plain),
      prefix + field("integer", grouped | self.graph_zero_padded),
      self.negative + field("integer", grouped),
    )
    self.fst = self.add_tokens(graph).optimize()

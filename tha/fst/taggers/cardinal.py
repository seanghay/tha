import pynini
from pynini.lib import pynutil, rewrite

from tha.fst.graph_utils import (
  SEP,
  TH_DIGIT,
  TH_NON_ZERO,
  GraphFst,
  field,
  insert_sep,
  load,
  load_pairs,
)

# the "−" (U+2212) sign is what the pre-processor rewrites a hyphen into when
# it is really a minus sign, see `tha.fst.normalizer`
MINUS = "−"

# numbers with more digits than this are read digit by digit
MAX_DIGITS = 15


class CardinalFst(GraphFst):
  """
  Integers, e.g.
    1234      -> cardinal { integer: "មួយពាន់▁ពីររយ▁សាមសិបបួន" }
    −5        -> cardinal { negative: "true" integer: "ប្រាំ" }
    1,000,000 -> cardinal { integer: "មួយលាន" }
    007       -> cardinal { integer: "សូន្យ▁សូន្យ▁ប្រាំពីរ" }
    #5        -> cardinal { prefix: "លេខ" integer: "ប្រាំ" }
    ០៩        -> cardinal { integer: "ប្រាំបួន" }
    1.000.000 -> cardinal { integer: "មួយលាន" grouping: "dot" }
  """

  def __init__(self):
    super().__init__(name="cardinal", kind="classify")

    digit = load("digit.tsv")
    zero = load("zero.tsv")
    ties = load("ties.tsv")
    magnitudes = {int(e): w for e, w in load_pairs("magnitudes.tsv")}

    # `nz[k]` reads k-digit strings whose first digit isn't 0,
    # `full[k]` reads any k-digit string ("" when all zeros).
    nz = {1: digit}
    full = {1: nz[1] | pynutil.delete("0")}

    nz[2] = ties + (pynutil.delete("0") | digit)
    full[2] = nz[2] | (pynutil.delete("0") + full[1])

    for k in range(3, MAX_DIGITS + 1):
      e = max(m for m in magnitudes if m <= k - 1)
      tail_non_zero = pynini.difference(TH_DIGIT**e, "0" * e).optimize() @ full[e]
      tail = pynutil.delete("0" * e) | (insert_sep + tail_non_zero)
      nz[k] = (nz[k - e] + pynutil.insert(magnitudes[e]) + tail).optimize()
      full[k] = (nz[k] | (pynutil.delete("0") + full[k - 1])).optimize()

    graph = pynini.union(zero, *(nz[k] for k in range(1, MAX_DIGITS + 1))).optimize()
    graph_no_zero = pynini.difference(graph.copy().project("input"), "0") @ graph

    # 1,000,000 and 1 000 000 (a space is the usual separator in Khmer text)
    def grouped(sep):
      return (
        pynini.closure(TH_DIGIT, 1, 3)
        + pynini.closure(pynutil.delete(sep) + TH_DIGIT**3, 1)
      ) @ graph

    graph_grouped_space = grouped(" ").optimize()
    graph_grouped = (grouped(",") | graph_grouped_space).optimize()
    # 1.000.000, common in Khmer text. 0.004 can't match (no leading zero)
    graph_grouped_dot = grouped(".").optimize()

    single_digit = zero | digit
    digits = (single_digit + pynini.closure(insert_sep + single_digit)).optimize()
    # 007, or anything too long to read as a number
    leading_zeros = "0" + pynini.closure(TH_DIGIT, 2)
    too_long = TH_NON_ZERO + pynini.closure(TH_DIGIT, MAX_DIGITS)
    graph_digits = ((leading_zeros | too_long) @ digits).optimize()
    # ថ្ងៃទី០៩, ០៥ថ្ងៃ: a zero padded two digit number is read as the number
    padded_two = (pynutil.delete("0") + digit) | pynini.cross("00", "សូន្យ▁សូន្យ")

    # reusable graphs for the other classes
    self.graph = graph  # plain integer without leading zeros
    self.graph_with_grouping = (graph | graph_grouped).optimize()
    # a comma decimal (1 000,5) can't have comma grouping
    self.graph_with_space_grouping = (graph | graph_grouped_space).optimize()
    self.graph_grouped_dot = graph_grouped_dot
    self.digits = digits  # digit by digit
    self.single_digit = single_digit
    # leading zeros are read one by one, the rest as a number: 05 -> សូន្យ▁ប្រាំ
    zeros = pynini.cross("0", "សូន្យ")
    self.graph_zero_padded = (
      (pynini.closure(zeros + insert_sep) + graph_no_zero)
      | (zeros + pynini.closure(insert_sep + zeros))
    ).optimize()

    # any digit string: zero padded groups as above, very long ones digit by digit
    self.graph_any = (
      self.graph_zero_padded | (pynini.closure(TH_DIGIT, MAX_DIGITS + 1) @ digits)
    ).optimize()

    optional_minus = pynini.closure(
      pynutil.insert('negative: "true" ') + pynutil.delete(MINUS), 0, 1
    )
    integer = field("integer", self.graph_with_grouping | graph_digits | padded_two)
    # marked, so that a following scale word can reject it: ២.១៦៦លាន is 2.166
    # million, not 2166 million (see ClassifyFst.filter)
    integer_dot = field("integer", graph_grouped_dot) + pynutil.insert(
      ' grouping: "dot"'
    )
    integer |= integer_dot
    # #5, No. 5 -> លេខ▁ប្រាំ (№ is a symbol, see symbols.tsv)
    number_sign = pynini.cross(
      pynini.union("#", "No.", "no.", "Nº", "№"), 'prefix: "លេខ" '
    )
    number_sign += pynini.closure(pynutil.delete(" "), 0, 1)
    # "លេខ#190": don't say លេខ twice
    number_sign = (
      pynini.closure(
        pynutil.delete("លេខ") + pynini.closure(pynutil.delete(" "), 0, 1), 0, 1
      )
      + number_sign
    )
    graph = (optional_minus | number_sign) + integer
    self.fst = self.add_tokens(graph).optimize()

  def words(self, number) -> str:
    return rewrite.top_rewrite(str(number), self.graph)


def join(*parts: pynini.Fst) -> pynini.Fst:
  """Concatenates graphs with the in-token separator between them."""
  out = parts[0]
  for p in parts[1:]:
    out = out + pynutil.insert(SEP) + p
  return out

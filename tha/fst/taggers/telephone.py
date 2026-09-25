import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import TH_DIGIT, TH_NON_ZERO, GraphFst, field, insert_sep
from tha.fst.taggers.cardinal import CardinalFst


class TelephoneFst(GraphFst):
  """
  Cambodian phone numbers: 0 + a two digit prefix + 6 or 7 digits, or the same
  with +855 instead of the 0. The subscriber part is read in chunks of two,
  the last chunk takes the remaining digit.
    012 345 678   -> telephone { number_part: "សូន្យ▁ដប់ពីរ▁សាមសិបបួន▁ហាសិបប្រាំមួយ▁ចិតសិបប្រាំបី" }
    +855 96 123 4567 -> telephone { number_part: "សូន្យ▁កៅសិបប្រាំមួយ▁ដប់ពីរ▁សាមសិបបួន▁ប្រាំរយ▁ហុកសិបប្រាំពីរ" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="telephone", kind="classify")

    sep = pynini.union(" ", "-", ".")
    prefix = (TH_NON_ZERO + TH_DIGIT) @ cardinal.graph
    chunk2 = TH_DIGIT**2 @ cardinal.graph_zero_padded
    chunk3 = TH_DIGIT**3 @ cardinal.graph_zero_padded
    subscriber = (chunk2 + insert_sep + chunk2 + insert_sep + chunk2) | (
      chunk2 + insert_sep + chunk2 + insert_sep + chunk3
    )
    # digits with at most one separator between any two of them
    digits_with_sep = TH_DIGIT + pynini.closure(pynutil.delete(sep).ques + TH_DIGIT)
    subscriber = (digits_with_sep @ subscriber).optimize()

    country = pynini.union("+855", "(+855)", "+(855)")
    # (023) 123 456
    parens = (
      pynutil.delete("(")
      + pynini.cross("0", "សូន្យ")
      + insert_sep
      + prefix
      + pynutil.delete(")")
    )
    start = pynini.cross("0", "សូន្យ") | (
      pynini.cross(country, "សូន្យ") + pynutil.delete(sep).ques + pynutil.delete("0").ques
    )
    graph = (
      ((start + insert_sep + prefix) | parens)
      + pynutil.delete(sep).ques
      + insert_sep
      + subscriber
    )
    self.fst = self.add_tokens(field("number_part", graph)).optimize()

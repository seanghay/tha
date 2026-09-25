import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, TH_DIGIT, GraphFst, field, insert_sep
from tha.fst.taggers.cardinal import CardinalFst
from tha.fst.taggers.code import spelled_letters

SQUARE = "ការ៉េ"


class LicensePlateFst(GraphFst):
  """
  Cambodian license plates, e.g.
    2A-1234 -> license_plate { value: "ពីរ▁អេ▁ដប់ពីរ▁សាមសិបបួន" }
    1AB 4444 -> license_plate { value: "មួយ▁អេ▁ប៊ី▁ការ៉េ▁បួន" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="license_plate", kind="classify")

    province = pynini.closure(TH_DIGIT, 1, 2) @ cardinal.graph_zero_padded
    letters = spelled_letters(2)
    pair = TH_DIGIT**2 @ cardinal.graph_zero_padded
    square = pynini.union(
      *[
        pynini.cross(d * 4, SQUARE + SEP) + pynutil.insert(cardinal.words(d))
        for d in "0123456789"
      ]
    )
    number = pynutil.add_weight(pair + insert_sep + pair, 0.01) | square
    graph = (
      province
      + insert_sep
      + letters
      + pynutil.delete(pynini.union("-", " "))
      + insert_sep
      + number
    )
    self.fst = self.add_tokens(field("value", graph)).optimize()

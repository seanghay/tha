import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import TH_DIGIT, GraphFst, field, load
from tha.fst.itn.taggers.cardinal import CardinalFst
from tha.fst.taggers.license_plate import SQUARE


class LicensePlateFst(GraphFst):
  """
  ពីរអេប៊ីការ៉េបួន           -> license_plate { value: "2AB-4444" }
  ពីរអេដប់ពីរសាមសិបបួន       -> license_plate { value: "2A-1234" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="license_plate", kind="classify")

    province = cardinal.graph_any @ pynini.closure(TH_DIGIT, 1, 2)
    letter = pynini.invert(load("latin_letters.tsv"))
    pair = cardinal.graph_any @ TH_DIGIT**2
    # ការ៉េបួន: four times the same digit
    repeated = pynini.string_map([(d, d * 4) for d in "0123456789"])
    square = pynutil.delete(SQUARE) + ((cardinal.digit | cardinal.zero) @ repeated)
    number = (pair + pair) | square
    graph = province + letter + letter.ques + pynutil.insert("-") + number
    self.fst = self.add_tokens(field("value", graph)).optimize()

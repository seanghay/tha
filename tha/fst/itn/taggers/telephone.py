import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import TH_DIGIT, GraphFst, field
from tha.fst.itn.taggers.cardinal import CardinalFst


class TelephoneFst(GraphFst):
  """
  Cambodian phone numbers read like the normalizer does: 0, the two digit
  prefix, then the subscriber number in chunks of two (three for the last one
  of a 7 digit number).
    សូន្យដប់ពីរសាមសិបបួនហាសិបប្រាំមួយចិតសិបប្រាំបី -> telephone { number_part: "012 345 678" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="telephone", kind="classify")

    def chunk(width):
      return (cardinal.graph_any @ TH_DIGIT**width).optimize()

    prefix = cardinal.graph_nz @ (pynini.union(*"123456789") + TH_DIGIT)
    subscriber = chunk(2) + chunk(2) + (chunk(2) | chunk(3))
    digits = cardinal.zero + prefix + subscriber
    # 012 345 678, 096 123 4567
    layout = (
      TH_DIGIT**3
      + pynutil.insert(" ")
      + TH_DIGIT**3
      + pynutil.insert(" ")
      + pynini.closure(TH_DIGIT, 3, 4)
    )
    self.fst = self.add_tokens(field("number_part", digits @ layout)).optimize()

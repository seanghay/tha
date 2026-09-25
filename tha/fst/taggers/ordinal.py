import pynini

from tha.fst.graph_utils import GraphFst, field
from tha.fst.taggers.cardinal import CardinalFst

SUFFIXES = ["st", "nd", "rd", "th"]


class OrdinalFst(GraphFst):
  """
  1st, 2ND, 21st -> ordinal { integer: "ម្ភៃមួយ" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="ordinal", kind="classify")
    suffix = pynini.union(
      *[v for s in SUFFIXES for v in (s, s.upper(), s.capitalize())]
    )
    graph = cardinal.graph + pynini.cross(suffix, "")
    self.fst = self.add_tokens(field("integer", graph)).optimize()

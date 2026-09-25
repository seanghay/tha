import pynini

from tha.fst.graph_utils import GraphFst, field
from tha.fst.itn.taggers.cardinal import CardinalFst
from tha.fst.normalizer import RANGE_WORD, SCORE_WORD


class RangeFst(GraphFst):
  """
  Ranges and scores of two numbers, single digits included:
    ពីរដល់បី    -> range { value: "2-3" }
    មួយទល់សូន្យ -> range { value: "1-0" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="range", kind="classify")
    dash = pynini.cross(pynini.union(RANGE_WORD, SCORE_WORD), "-")
    self.graph = (cardinal.graph_grouped + dash + cardinal.graph_grouped).optimize()
    self.fst = self.add_tokens(field("value", self.graph)).optimize()

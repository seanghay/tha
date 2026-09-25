import pynini

from tha.fst.graph_utils import GraphFst, field
from tha.fst.itn.taggers.cardinal import CardinalFst


class SerialFst(GraphFst):
  """
  Three or more numbers joined by "ចុច" (versions, IP addresses):
    មួយរយកៅសិបពីរចុចមួយរយហុកសិបប្រាំបីចុចសូន្យចុចមួយ -> serial { value: "192.168.0.1" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="serial", kind="classify")
    group = cardinal.graph_any
    graph = group + pynini.closure(pynini.cross("ចុច", ".") + group, 2)
    self.fst = self.add_tokens(field("value", graph)).optimize()

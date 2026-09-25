import pynini

from tha.fst.graph_utils import SEP, GraphFst, field
from tha.fst.taggers.cardinal import CardinalFst


class SerialFst(GraphFst):
  """
  Three or more digit groups joined by dots (versions, IP addresses) or
  commas (lists), each group is read on its own.
    1.2.10      -> serial { value: "មួយ▁ចុច▁ពីរ▁ចុច▁ដប់" }
    192.168.0.1 -> serial { value: "មួយរយ▁កៅសិបពីរ▁ចុច▁...▁ចុច▁មួយ" }
    1,2,3       -> serial { value: "មួយ,ពីរ,បី" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="serial", kind="classify")
    group = cardinal.graph_any

    def groups(sep, spoken):
      return group + pynini.closure(pynini.cross(sep, spoken) + group, 2)

    graph = groups(".", f"{SEP}ចុច{SEP}") | groups(",", ",")
    self.fst = self.add_tokens(field("value", graph)).optimize()

from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, GraphFst, delete_field, delete_space
from tha.fst.verbalizers.cardinal import optional_negative


class MeasureFst(GraphFst):
  """measure { quantity: "ប្រាំ" units: "គីឡូម៉ែត្រ" } -> ប្រាំ▁គីឡូម៉ែត្រ"""

  def __init__(self):
    super().__init__(name="measure", kind="verbalize")
    graph = (
      optional_negative()
      + delete_field("quantity")
      + delete_space
      + pynutil.insert(SEP)
      + delete_field("units")
    )
    self.fst = self.delete_tokens(graph).optimize()

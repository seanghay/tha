from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, GraphFst, delete_field, delete_space
from tha.fst.verbalizers.cardinal import optional_negative


class DecimalFst(GraphFst):
  """decimal { integer_part: "មួយ" point: "ចុច" fractional_part: "ប្រាំ" } -> មួយ▁ចុច▁ប្រាំ"""

  def __init__(self):
    super().__init__(name="decimal", kind="verbalize")
    sep = delete_space + pynutil.insert(SEP)
    graph = (
      optional_negative()
      + delete_field("integer_part")
      + sep
      + delete_field("point")
      + sep
      + delete_field("fractional_part")
    )
    self.fst = self.delete_tokens(graph).optimize()

from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, GraphFst, delete_field, delete_space


class RomanFst(GraphFst):
  """roman { prefix: "ទី" integer: "ប្រាំពីរ" } -> ទី▁ប្រាំពីរ"""

  def __init__(self):
    super().__init__(name="roman", kind="verbalize")
    graph = (
      delete_field("prefix")
      + delete_space
      + pynutil.insert(SEP)
      + delete_field("integer")
    )
    self.fst = self.delete_tokens(graph).optimize()

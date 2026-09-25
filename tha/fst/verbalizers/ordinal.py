from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, GraphFst, delete_field


class OrdinalFst(GraphFst):
  """ordinal { integer: "មួយ" } -> ទី▁មួយ"""

  def __init__(self):
    super().__init__(name="ordinal", kind="verbalize")
    graph = pynutil.insert("ទី" + SEP) + delete_field("integer")
    self.fst = self.delete_tokens(graph).optimize()

from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, GraphFst, delete_field, delete_space
from tha.fst.taggers.electronic import AT


class ElectronicFst(GraphFst):
  """electronic { username: "john" domain: "g▁mail▁dot▁com" } -> john▁at▁g▁mail▁dot▁com"""

  def __init__(self):
    super().__init__(name="electronic", kind="verbalize")
    user = delete_field("username") + delete_space + pynutil.insert(f"{SEP}{AT}{SEP}")
    graph = user.ques + delete_field("domain")
    self.fst = self.delete_tokens(graph).optimize()

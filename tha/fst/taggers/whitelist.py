from tha.fst.graph_utils import GraphFst, field, load


class WhiteListFst(GraphFst):
  """Fixed abbreviations from whitelist.tsv, e.g. ព.ស. -> ពុទ្ធសករាជ"""

  def __init__(self):
    super().__init__(name="whitelist", kind="classify")
    self.fst = self.add_tokens(field("value", load("whitelist.tsv"))).optimize()

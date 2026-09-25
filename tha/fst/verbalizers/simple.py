from tha.fst.graph_utils import GraphFst, delete_field


class SingleFieldFst(GraphFst):
  """Classes whose tagger already produced the spoken form in one field."""

  def __init__(self, name: str, key: str):
    super().__init__(name=name, kind="verbalize")
    self.fst = self.delete_tokens(delete_field(key)).optimize()

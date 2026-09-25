import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, GraphFst, delete_field, delete_space

NEGATIVE = "ដក"


def optional_negative():
  return pynini.closure(
    pynini.cross('negative: "true"', NEGATIVE + SEP) + delete_space, 0, 1
  )


class CardinalFst(GraphFst):
  """cardinal { negative: "true" integer: "ប្រាំ" } -> ដក▁ប្រាំ"""

  def __init__(self):
    super().__init__(name="cardinal", kind="verbalize")
    prefix = delete_field("prefix") + delete_space + pynutil.insert(SEP)
    self.fst = self.delete_tokens(
      (optional_negative() | prefix.ques)
      + delete_field("integer")
      + (delete_space + pynutil.delete('grouping: "dot"')).ques
    ).optimize()

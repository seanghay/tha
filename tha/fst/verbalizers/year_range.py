from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, GraphFst, delete_field, delete_space

RANGE_WORD = "ដល់"


class YearRangeFst(GraphFst):
  """year_range { start: "ពីរពាន់▁ម្ភៃ" end: "ពីរពាន់▁ម្ភៃមួយ" } -> ពីរពាន់▁ម្ភៃ▁ដល់▁ពីរពាន់▁ម្ភៃមួយ"""

  def __init__(self):
    super().__init__(name="year_range", kind="verbalize")
    graph = (
      delete_field("start")
      + delete_space
      + pynutil.insert(f"{SEP}{RANGE_WORD}{SEP}")
      + delete_field("end")
    )
    self.fst = self.delete_tokens(graph).optimize()

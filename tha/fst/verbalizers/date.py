from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, GraphFst, delete_field, delete_space

DAY = "ថ្ងៃទី"
MONTH = "ខែ"
YEAR = "ឆ្នាំ"


class DateFst(GraphFst):
  """date { day: "ពីរ" month: "មករា" year: "ពីរពាន់▁ម្ភៃបួន" } -> ថ្ងៃទី▁ពីរ▁ខែ▁មករា▁ឆ្នាំ▁ពីរពាន់▁ម្ភៃបួន
  The tagger's field order is normalized to day, month, year beforehand."""

  def __init__(self):
    super().__init__(name="date", kind="verbalize")
    sep = delete_space + pynutil.insert(SEP)
    graph = (
      pynutil.insert(DAY + SEP)
      + delete_field("day")
      + sep
      + pynutil.insert(MONTH + SEP)
      + delete_field("month")
      + sep
      + pynutil.insert(YEAR + SEP)
      + delete_field("year")
    )
    self.fst = self.delete_tokens(graph).optimize()

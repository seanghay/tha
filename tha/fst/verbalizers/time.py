from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, GraphFst, delete_field, delete_space

HOUR = "ម៉ោង"
MINUTE = "នាទី"
SECOND = "វិនាទី"


class TimeFst(GraphFst):
  """time { hours: "ដប់" minutes: "ម្ភៃបី" period: "ព្រឹក" } -> ម៉ោង▁ដប់▁ម្ភៃបី▁នាទី▁ព្រឹក"""

  def __init__(self):
    super().__init__(name="time", kind="verbalize")
    sep = delete_space + pynutil.insert(SEP)
    graph = (
      pynutil.insert(HOUR + SEP)
      + delete_field("hours")
      + (sep + delete_field("minutes") + pynutil.insert(SEP + MINUTE)).ques
      + (sep + delete_field("seconds") + pynutil.insert(SEP + SECOND)).ques
      + (sep + delete_field("period")).ques
    )
    self.fst = self.delete_tokens(graph).optimize()

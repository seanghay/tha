import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import GraphFst, field
from tha.fst.itn.taggers.cardinal import CardinalFst
from tha.fst.verbalizers.fraction import AND
from tha.fst.verbalizers.time import HOUR, MINUTE, SECOND

HALF = "កន្លះ"


def _padded(cardinal: CardinalFst, values) -> pynini.Fst:
  return (
    cardinal.graph @ pynini.string_map([(str(v), f"{v:02d}") for v in values])
  ).optimize()


class TimeFst(GraphFst):
  """
  Clock times after "ម៉ោង", the period (ព្រឹក, យប់, ...) is left as a word:
    ម៉ោងដប់               -> time { hours: "10" minutes: "00" }
    ម៉ោងដប់ម្ភៃបីនាទី       -> time { hours: "10" minutes: "23" }
    ម៉ោងប្រាំបីសាមសិប       -> time { hours: "8" minutes: "30" }
    ម៉ោងប្រាំបីកន្លះ         -> time { hours: "8" minutes: "30" }
    ម៉ោងដប់សូន្យនាទីប្រាំវិនាទី -> time { hours: "10" minutes: "00" seconds: "05" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="time", kind="classify")

    hours = cardinal.graph @ pynini.string_map([str(h) for h in range(25)])
    sixty = _padded(cardinal, range(60))
    sp = pynutil.insert(" ")

    def minute(values):
      return sp + field("minutes", _padded(cardinal, values))

    # "ម៉ោងដប់ពីរ" is 12 o'clock, so minutes below 10 need "នាទី"
    # "ម៉ោងប្រាំបី និងសាមសិបនាទី"
    minutes = pynini.union(
      pynutil.delete(AND).ques + minute(range(1, 60)) + pynutil.delete(MINUTE),
      minute(range(10, 60)),
      sp + field("minutes", pynini.cross(HALF, "30")),
      sp + field("minutes", pynutil.insert("00")),
    )
    seconds = (
      sp
      + field("minutes", sixty)
      + pynutil.delete(MINUTE)
      + sp
      + field("seconds", sixty)
      + pynutil.delete(SECOND)
    )
    # "ម៉ោងប្រាំបួន ប្រាំពីរវិនាទី": 9:00:07
    seconds |= (
      sp
      + field("minutes", pynutil.insert("00"))
      + sp
      + field("seconds", _padded(cardinal, range(1, 60)))
      + pynutil.delete(SECOND)
    )
    graph = pynutil.delete(HOUR) + field("hours", hours) + (minutes | seconds)
    self.fst = self.add_tokens(graph).optimize()

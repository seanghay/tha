import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import GraphFst, delete_space_opt, field
from tha.fst.taggers.cardinal import CardinalFst


def _period(hour: int, pm: bool) -> str:
  if not pm:
    return "យប់" if hour == 12 else "ព្រឹក"
  if hour == 12:
    return "ថ្ងៃត្រង់"
  if hour <= 4:
    return "រសៀល"
  if hour <= 6:
    return "ល្ងាច"
  return "យប់"


AM = ["AM", "am", "Am", "A.M.", "a.m."]
PM = ["PM", "pm", "Pm", "P.M.", "p.m."]


class TimeFst(GraphFst):
  """
  24h or 12h clock times, e.g.
    10:23      -> time { hours: "ដប់" minutes: "ម្ភៃបី" }
    9:05:30 pm -> time { hours: "ប្រាំបួន" minutes: "ប្រាំ" seconds: "សាមសិប"
                         period: "យប់" }
    10:00      -> time { hours: "ដប់" }
    5pm        -> time { hours: "ប្រាំ" period: "ល្ងាច" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="time", kind="classify")

    def hour_strings(h):
      return [str(h), f"{h:02d}"] if h < 10 else [str(h)]

    def hour_graph(hours):
      return pynini.string_map(
        [(s, cardinal.words(h)) for h in hours for s in hour_strings(h)]
      )

    sixty = pynini.string_map(
      [(f"{m:02d}", cardinal.words(m)) for m in range(60)]
    ).optimize()
    non_zero_sixty = pynini.string_map(
      [(f"{m:02d}", cardinal.words(m)) for m in range(1, 60)]
    ).optimize()

    sp = pynutil.insert(" ")
    minutes = pynutil.delete(":") + sp + field("minutes", non_zero_sixty)
    minutes_zero = pynutil.delete(":00")
    seconds = (
      pynutil.delete(":")
      + sp
      + field("minutes", sixty)
      + pynutil.delete(":")
      + sp
      + field("seconds", sixty)
    )
    clock = minutes | minutes_zero | seconds
    # 8h30, the French way of writing it that is common in Cambodia
    h_clock = pynutil.delete(pynini.union("h", "H")) + (
      (sp + field("minutes", non_zero_sixty)) | pynutil.delete("00")
    )

    graph_24 = field("hours", hour_graph(range(0, 25))) + (clock | h_clock)

    graphs_12 = []
    for h in range(1, 13):
      for suffixes, pm in ((AM, False), (PM, True)):
        graphs_12.append(
          field("hours", hour_graph([h]))
          + clock.ques
          + delete_space_opt
          + pynutil.delete(pynini.union(*suffixes))
          + sp
          + field("period", pynutil.insert(_period(h, pm)))
        )

    # the verbalizer says "ម៉ោង", don't say it twice for "ម៉ោង 10:30"
    prefix = (pynutil.delete("ម៉ោង") + delete_space_opt).ques
    graph = graph_24 | pynini.union(*graphs_12)
    self.fst = self.add_tokens(prefix + graph).optimize()

import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import (
  TH_DIGIT,
  TH_NON_ZERO,
  GraphFst,
  delete_space_opt,
  field,
  load_pairs,
)
from tha.fst.taggers.cardinal import CardinalFst

# the verbalizer says "ថ្ងៃទី", so it is dropped from the text right before a
# date to not say it twice: "ថ្ងៃទី 02/01/2024"
PREFIX = pynini.union("ថ្ងៃទី", "ថ្ងៃ")


class DateFst(GraphFst):
  """
  Numeric dates separated by "-", "/" or "." (the same one twice). Fields are
  tagged in input order and reordered to day, month, year before verbalizing.
    2024-01-02 -> date { year: "ពីរពាន់▁ម្ភៃបួន" month: "មករា" day: "ពីរ" }
    02/01/2024 -> date { day: "ពីរ" month: "មករា" year: "ពីរពាន់▁ម្ភៃបួន" }
  Day first is the norm in Cambodia, month first is only accepted when the
  first part can't be a month (01/13/2024).
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="date", kind="classify")

    def padded(values, words):
      return pynini.string_map(
        [(s, words(v)) for v in values for s in {str(v), f"{v:02d}"}]
      ).optimize()

    months = dict(load_pairs("months.tsv"))
    month = field("month", padded(range(1, 13), lambda m: months[str(m)]))
    day = field("day", padded(range(1, 32), cardinal.words))
    day_13 = field("day", padded(range(13, 32), cardinal.words))
    year = field("year", (TH_NON_ZERO + TH_DIGIT**3) @ cardinal.graph)

    graphs = []
    for sep in "-/.":
      s = pynutil.delete(sep) + pynutil.insert(" ")
      graphs.append(year + s + month + s + day)
      graphs.append(day + s + month + s + year)
      graphs.append(month + s + day_13 + s + year)

    prefix = (pynutil.delete(PREFIX) + delete_space_opt).ques
    self.fst = self.add_tokens(prefix + pynini.union(*graphs)).optimize()

import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import TH_DIGIT, TH_NON_ZERO, GraphFst, field, load_pairs
from tha.fst.itn.taggers.cardinal import CardinalFst
from tha.fst.verbalizers.date import DAY, MONTH, YEAR


class DateFst(GraphFst):
  """
  Full dates, day first as usual in Cambodia:
    ថ្ងៃទីពីរ ខែមករា ឆ្នាំពីរពាន់ម្ភៃបួន -> date { day: "02" month: "01" year: "2024" }
  "ខែ" and "ឆ្នាំ" may be left out, and a space may separate the parts. A day without a year is left to the
  cardinal grammar: ថ្ងៃទីពីរ ខែមករា -> ថ្ងៃទី2 ខែមករា
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="date", kind="classify")

    day = cardinal.graph @ pynini.string_map(
      [(str(d), f"{d:02d}") for d in range(1, 32)]
    )
    month = pynini.string_map(
      [(word, f"{int(m):02d}") for m, word in load_pairs("months.tsv")]
    )
    year = cardinal.graph @ (TH_NON_ZERO + TH_DIGIT**3)
    sp = pynutil.insert(" ")
    # dates are written with a space between their parts:
    # ថ្ងៃទីដប់បី ខែមករា ឆ្នាំពីរពាន់ម្ភៃបួន
    part = pynutil.delete(" ").ques
    graph = (
      pynutil.delete(DAY)
      + field("day", day)
      + sp
      + part
      + pynutil.delete(MONTH).ques
      + field("month", month)
      + sp
      + part
      + pynutil.delete(YEAR).ques
      + field("year", year)
    )
    self.fst = self.add_tokens(graph).optimize()

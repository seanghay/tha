import pynini

from tha.fst.graph_utils import TH_DIGIT, GraphFst, field
from tha.fst.taggers.cardinal import CardinalFst

FIRST_YEAR, LAST_YEAR = 1900, 2100
MAX_SPAN = 50


class YearRangeFst(GraphFst):
  """
  Ranges of years and football seasons, always read as a range (never a
  score or a fraction):
    2020-2021 -> year_range { start: "ពីរពាន់▁ម្ភៃ" end: "ពីរពាន់▁ម្ភៃមួយ" }
    2022/23   -> year_range { start: "ពីរពាន់▁ម្ភៃពីរ" end: "ពីរពាន់▁ម្ភៃបី" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="year_range", kind="classify")

    # which pairs are valid, expanded to 4 digit years: "2022/23" -> "2022/2023"
    pairs = []
    for a in range(FIRST_YEAR, LAST_YEAR):
      for b in range(a + 1, min(a + MAX_SPAN, LAST_YEAR) + 1):
        for sep in ("-", "–", "/"):
          pairs.append((f"{a}{sep}{b}", f"{a}/{b}"))
      b = a + 1
      if b // 100 == a // 100:
        pairs.append((f"{a}/{b % 100:02d}", f"{a}/{b}"))
    valid = pynini.string_map(pairs).optimize()

    year = TH_DIGIT**4 @ cardinal.graph
    spoken = field("start", year) + pynini.cross("/", " ") + field("end", year)
    self.fst = self.add_tokens((valid @ spoken).optimize()).optimize()

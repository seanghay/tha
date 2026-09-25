import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import TH_DIGIT, GraphFst, field
from tha.fst.itn.taggers.cardinal import CardinalFst
from tha.fst.taggers.decimal import POINT_WORDS

# the fractional part is at most this many digits once read as a number, so
# that "ប្រាំចុចប្រាំលាន" is 5.5 + លាន and not 5.5000000
MAX_FRACTIONAL = 6


class DecimalFst(GraphFst):
  """
  ដប់ពីរចុចប្រាំ          -> decimal { integer_part: "12" point: "." fractional_part: "5" }
  សូន្យចុចសូន្យសូន្យមួយ   -> decimal { integer_part: "0" point: "." fractional_part: "001" }
  មួយក្បៀសប្រាំ           -> decimal { integer_part: "1" point: "," fractional_part: "5" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="decimal", kind="classify")

    # zeros are read one by one, then the rest as a number: .001 -> សូន្យសូន្យមួយ
    self.fractional = (
      cardinal.graph_any @ pynini.closure(TH_DIGIT, 1, MAX_FRACTIONAL)
    ).optimize()
    point = pynini.string_map([(w, p) for p, w in POINT_WORDS.items()])

    self.integer_part = field("integer_part", cardinal.graph_grouped)
    self.graph = (
      self.integer_part
      + pynutil.insert(" ")
      + field("point", point)
      + pynutil.insert(" ")
      + field("fractional_part", self.fractional)
    ).optimize()
    self.fst = self.add_tokens(cardinal.negative.ques + self.graph).optimize()

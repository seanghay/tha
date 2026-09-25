import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import GraphFst, field, insert_sep
from tha.fst.taggers.cardinal import MINUS, CardinalFst

POINT_WORDS = {".": "ចុច", ",": "ក្បៀស"}


class DecimalFst(GraphFst):
  """
  Decimal numbers, the fractional part is read like a number after its leading
  zeros, e.g.
    123.001 -> decimal { integer_part: "មួយរយ▁ម្ភៃបី" point: "ចុច"
                         fractional_part: "សូន្យ▁សូន្យ▁មួយ" }
    −1,5    -> decimal { negative: "true" integer_part: "មួយ" point: "ក្បៀស"
                         fractional_part: "ប្រាំ" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="decimal", kind="classify")

    fractional = cardinal.graph_any

    # 1,000.5 has a grouped integer part, a comma decimal (1,5) can't
    integer_dot = cardinal.graph_with_grouping
    integer_comma = cardinal.graph_with_space_grouping | cardinal.graph_grouped_dot

    def build(integer, point):
      return (
        field("integer_part", integer)
        + pynutil.insert(" ")
        + field("point", pynini.cross(point, POINT_WORDS[point]))
        + pynutil.insert(" ")
        + field("fractional_part", fractional)
      )

    graph = build(integer_dot, ".") | build(integer_comma, ",")
    optional_minus = pynini.closure(
      pynutil.insert('negative: "true" ') + pynutil.delete(MINUS), 0, 1
    )
    self.fst = self.add_tokens(optional_minus + graph).optimize()

    # spoken form without the tagging, used by money/measure
    def words(integer, point):
      return (
        integer
        + insert_sep
        + pynini.cross(point, POINT_WORDS[point])
        + insert_sep
        + fractional
      )

    self.graph_words = (words(integer_dot, ".") | words(integer_comma, ",")).optimize()
    self.fractional = fractional

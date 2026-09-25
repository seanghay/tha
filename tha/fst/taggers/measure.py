import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import GraphFst, delete_space_opt, field, load
from tha.fst.taggers.cardinal import MINUS, CardinalFst
from tha.fst.taggers.decimal import DecimalFst


class MeasureFst(GraphFst):
  """
  A number followed by a unit (measure.tsv), percentages included, e.g.
    5km   -> measure { quantity: "ប្រាំ" units: "គីឡូម៉ែត្រ" }
    12.5% -> measure { quantity: "ដប់ពីរ▁ចុច▁ប្រាំ" units: "ភាគរយ" }
  """

  def __init__(self, cardinal: CardinalFst, decimal: DecimalFst):
    super().__init__(name="measure", kind="classify")
    units = load("measure.tsv")
    # 1,500% is fifteen hundred, like a plain cardinal
    quantity = cardinal.graph_with_grouping | pynutil.add_weight(
      decimal.graph_words, 0.1
    )
    optional_minus = pynini.closure(
      pynutil.insert('negative: "true" ') + pynutil.delete(MINUS), 0, 1
    )
    graph = (
      optional_minus
      + field("quantity", quantity)
      + delete_space_opt
      + pynutil.insert(" ")
      + field("units", units)
    )
    self.fst = self.add_tokens(graph).optimize()

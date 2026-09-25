import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import GraphFst, field, load_pairs
from tha.fst.itn.taggers.cardinal import CardinalFst
from tha.fst.itn.taggers.decimal import DecimalFst
from tha.fst.itn.taggers.range import RangeFst

# written unit of each spoken one, the first in measure.tsv unless set here
PREFERRED = {"លីត្រ": "L", "គីឡូ": "kg"}
# "ប្រាំនាទី" stays a Khmer word, "ផោន" is read as money
SKIPPED = {"នាទី", "ផោន"}


def units() -> pynini.Fst:
  written = dict(PREFERRED)
  for key, word in load_pairs("measure.tsv"):
    if word not in SKIPPED:
      written.setdefault(word, key)
  return pynini.string_map(written.items()).optimize()


class MeasureFst(GraphFst):
  """
  ប្រាំគីឡូម៉ែត្រ         -> measure { integer_part: "5" units: "km" }
  ដប់ពីរចុចប្រាំភាគរយ    -> measure { integer_part: "12" point: "." fractional_part: "5" units: "%" }
  ប្រាំដល់ដប់ភាគរយ        -> measure { integer_part: "5-10" units: "%" }
  """

  def __init__(self, cardinal: CardinalFst, decimal: DecimalFst, range_: RangeFst):
    super().__init__(name="measure", kind="classify")
    integer = cardinal.graph_grouped | range_.graph
    quantity = decimal.graph | field("integer_part", integer)
    graph = (
      cardinal.negative.ques + quantity + pynutil.insert(" ") + field("units", units())
    )
    self.fst = self.add_tokens(graph).optimize()

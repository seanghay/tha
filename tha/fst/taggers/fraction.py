import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import GraphFst, delete_space_opt, field, load
from tha.fst.taggers.cardinal import MINUS, CardinalFst


class FractionFst(GraphFst):
  """
  Fractions, the numerator is read first as in Khmer, e.g.
    1/2  -> fraction { numerator: "មួយ" denominator: "ពីរ" }
    ¾    -> fraction { numerator: "បី" denominator: "បួន" }
    1½   -> fraction { integer_part: "មួយ" numerator: "មួយ" denominator: "ពីរ" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="fraction", kind="classify")

    non_zero = pynini.difference(cardinal.graph.copy().project("input"), "0")
    numerator = field("numerator", cardinal.graph)
    denominator = field("denominator", non_zero @ cardinal.graph)
    slash = numerator + pynutil.delete("/") + pynutil.insert(" ") + denominator

    # ½ -> 1/2 -> spoken
    vulgar = (load("fractions.tsv") @ slash).optimize()
    mixed = (
      field("integer_part", cardinal.graph)
      + delete_space_opt
      + pynutil.insert(" ")
      + vulgar
    )

    optional_minus = pynini.closure(
      pynutil.insert('negative: "true" ') + pynutil.delete(MINUS), 0, 1
    )
    graph = optional_minus + (slash | vulgar | mixed)
    self.fst = self.add_tokens(graph).optimize()

import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import GraphFst, delete_space_opt, field, load_pairs
from tha.fst.taggers.cardinal import CardinalFst


def to_roman(n: int) -> str:
  out = []
  for value, numeral in (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
  ):
    while n >= value:
      out.append(numeral)
      n -= value
  return "".join(out)


class RomanFst(GraphFst):
  """
  Roman numerals, only right after a word that is followed by a number
  (roman_prefixes.tsv) so that e.g. the English "I" is left alone.
    ជ័យវរ្ម័នទី VII -> roman { prefix: "ទី" integer: "ប្រាំពីរ" } (after "ជ័យវរ្ម័ន")
    ជំពូក II        -> roman { prefix: "ជំពូក" integer: "ពីរ" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="roman", kind="classify")

    numerals = (
      pynini.string_map([(to_roman(n), str(n)) for n in range(1, 4000)])
      @ cardinal.graph
    ).optimize()
    prefixes = pynini.union(*[p for (p,) in load_pairs("roman_prefixes.tsv")])
    graph = (
      field("prefix", prefixes)
      + delete_space_opt
      + pynutil.insert(" ")
      + field("integer", numerals)
    )
    self.fst = self.add_tokens(graph).optimize()

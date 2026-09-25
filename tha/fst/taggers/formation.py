import itertools

import pynini

from tha.fst.graph_utils import SEP, GraphFst, field
from tha.fst.taggers.cardinal import CardinalFst


class FormationFst(GraphFst):
  """
  Football formations, 3 or 4 digits joined by "-" that add up to 10 outfield
  players, read without the dashes:
    4-4-2   -> formation { value: "បួន▁បួន▁ពីរ" }
    4-2-3-1 -> formation { value: "បួន▁ពីរ▁បី▁មួយ" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="formation", kind="classify")
    pairs = []
    for n in (3, 4):
      for combo in itertools.product(range(1, 7), repeat=n):
        if sum(combo) == 10:
          pairs.append(
            ("-".join(map(str, combo)), SEP.join(cardinal.words(d) for d in combo))
          )
    self.fst = self.add_tokens(field("value", pynini.string_map(pairs))).optimize()

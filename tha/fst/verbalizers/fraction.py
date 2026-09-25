from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, GraphFst, delete_field, delete_space
from tha.fst.verbalizers.cardinal import optional_negative

OVER = "ភាគ"
AND = "និង"


class FractionFst(GraphFst):
  """fraction { integer_part: "មួយ" numerator: "មួយ" denominator: "ពីរ" }
  -> មួយ▁និង▁មួយ▁ភាគ▁ពីរ"""

  def __init__(self):
    super().__init__(name="fraction", kind="verbalize")
    sep = delete_space + pynutil.insert(SEP)
    integer = delete_field("integer_part") + sep + pynutil.insert(AND + SEP)
    graph = (
      optional_negative()
      + integer.ques
      + delete_field("numerator")
      + sep
      + pynutil.insert(OVER + SEP)
      + delete_field("denominator")
    )
    self.fst = self.delete_tokens(graph).optimize()

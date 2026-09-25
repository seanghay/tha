from pynini.lib import pynutil

from tha.fst.graph_utils import GraphFst, field
from tha.fst.itn.taggers.cardinal import CardinalFst
from tha.fst.verbalizers.fraction import AND, OVER


class FractionFst(GraphFst):
  """
  បីភាគបួន            -> fraction { numerator: "3" denominator: "4" }
  មួយនិងមួយភាគពីរ     -> fraction { integer_part: "1" numerator: "1" denominator: "2" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="fraction", kind="classify")
    sp = pynutil.insert(" ")
    integer = field("integer_part", cardinal.graph_grouped) + pynutil.delete(AND) + sp
    graph = (
      integer.ques
      + field("numerator", cardinal.graph)
      + pynutil.delete(OVER)
      + sp
      + field("denominator", cardinal.graph_nz)
    )
    self.fst = self.add_tokens(graph).optimize()

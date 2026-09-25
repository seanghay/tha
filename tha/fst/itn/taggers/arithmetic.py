import pynini

from tha.fst.graph_utils import GraphFst, field
from tha.fst.itn.taggers.cardinal import CardinalFst

# the words the normalizer reads these symbols as (symbols.tsv), written back
# with a space on each side
OPERATORS = {"បូក": "+", "ដក": "-", "គុណ": "×", "ចែក": "÷"}
EQUALS = ("ស្មើ", "=")


class ArithmeticFst(GraphFst):
  """
  Numbers joined by operators, single digits included:
    ម្ភៃដកដប់          -> arithmetic { value: "20 - 10" }
    ពីរបូកបីស្មើប្រាំ   -> arithmetic { value: "2 + 3 = 5" }
  An operator word is only read as one between two numbers, so ចែករំលែក or
  បូកសរុប stay words.
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="arithmetic", kind="classify")

    def op(word, symbol):
      return pynini.cross(word, f" {symbol} ")

    number = cardinal.graph_grouped
    operator = pynini.union(*[op(w, s) for w, s in OPERATORS.items()])
    graph = number + pynini.closure(operator + number, 1) + (op(*EQUALS) + number).ques
    self.fst = self.add_tokens(field("value", graph)).optimize()

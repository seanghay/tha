from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, GraphFst, delete_field, delete_space
from tha.fst.verbalizers.cardinal import optional_negative


class MoneyFst(GraphFst):
  """money { integer_part: "មួយ" currency_maj: "ដុល្លារ" fractional_part: "ប្រាំ" currency_min: "សេន" }
  -> មួយ▁ដុល្លារ▁ប្រាំ▁សេន"""

  def __init__(self):
    super().__init__(name="money", kind="verbalize")
    sep = delete_space + pynutil.insert(SEP)
    major = (
      (delete_field("integer_part") | delete_field("amount"))
      + sep
      + delete_field("currency_maj")
    )
    minor = delete_field("fractional_part") + sep + delete_field("currency_min")
    graph = optional_negative() + (major | minor | (major + sep + minor))
    self.fst = self.delete_tokens(graph).optimize()

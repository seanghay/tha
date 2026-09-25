import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import SEP, TH_ALPHA, GraphFst, field, load_pairs
from tha.fst.itn.taggers.cardinal import CardinalFst
from tha.fst.taggers.electronic import AT, DOT

SPACE = pynutil.delete(" ").ques


def _spelled(pairs) -> pynini.Fst:
  """g▁mail / g mail -> gmail (a ▁ is removed by `flexible_joins`)"""
  return pynini.string_map(
    [(v.replace(SEP, j), k) for k, v in pairs for j in ("", " ")]
  ).optimize()


class ElectronicFst(GraphFst):
  """
  E-mails and domain names spoken with "dot" / "ចុច" and "at" / "អ៊ែត":
    john dot doe at g mail dot com -> electronic { value: "john.doe@gmail.com" }
    w▁w▁w▁dot▁moeys▁dot▁gov▁dot▁k▁h -> electronic { value: "www.moeys.gov.kh" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="electronic", kind="classify")

    def word(spoken, written):
      return SPACE + pynini.cross(pynini.union(*spoken), written) + SPACE

    dot = word([DOT, "ចុច"], ".")
    at = word([AT, "អ៊ែត"], "@")
    digit = cardinal.digit | cardinal.zero
    # "john▁dot▁doe": a spoken "dot" is cheaper than the letters d, o, t
    char = pynutil.add_weight(TH_ALPHA | digit, 0.01)
    label = _spelled(load_pairs("domain_words.tsv")) | pynini.closure(char | "-", 1)
    tld = _spelled(load_pairs("tld.tsv"))
    domain = pynini.closure(label + dot, 1) + tld

    plus = word(["បូក"], "+")
    user = pynini.closure(char | plus | "_", 1)
    username = user + pynini.closure(dot + user)
    graph = pynini.union(domain, username + at + domain)
    self.fst = self.add_tokens(field("value", graph)).optimize()

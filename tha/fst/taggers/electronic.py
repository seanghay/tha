import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import (
  SEP,
  TH_ALPHA,
  GraphFst,
  field,
  load_pairs,
)
from tha.fst.taggers.cardinal import CardinalFst

DOT = "dot"
AT = "at"


def _case_variants(pairs):
  out = {}
  for k, v in pairs:
    for variant in (k, k.lower(), k.upper(), k.capitalize()):
      out.setdefault(variant, v)
  return pynini.string_map(out.items()).optimize()


class ElectronicFst(GraphFst):
  """
  E-mails and domain names with a known TLD (tld.tsv), the scheme and a
  trailing slash are dropped.
    john.doe@gmail.com -> electronic { username: "john▁dot▁doe"
                                      domain: "g▁mail▁dot▁com" }
    https://www.moeys.gov.kh/ -> electronic { domain: "w▁w▁w▁dot▁moeys▁dot▁gov▁dot▁k▁h" }
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="electronic", kind="classify")

    digit = pynutil.insert(SEP) + cardinal.single_digit + pynutil.insert(SEP)
    dot = pynini.cross(".", f"{SEP}{DOT}{SEP}")

    label_plain = pynini.closure(TH_ALPHA | digit | "-", 1)
    label = _case_variants(load_pairs("domain_words.tsv")) | pynutil.add_weight(
      label_plain, 0.01
    )
    tld = _case_variants(load_pairs("tld.tsv"))
    domain = pynini.closure(label + dot, 1) + tld

    plus = pynini.cross("+", f"{SEP}បូក{SEP}")
    user_char = TH_ALPHA | digit | plus | pynini.union("_", "-")
    username = pynini.closure(user_char, 1) + pynini.closure(
      dot + pynini.closure(user_char, 1)
    )

    scheme = pynini.union(
      *[v + "://" for s in ("http", "https") for v in (s, s.upper(), s.capitalize())]
    )
    url = (
      pynutil.delete(scheme).ques + field("domain", domain) + pynutil.delete("/").ques
    )
    email = (
      field("username", username)
      + pynutil.delete("@")
      + pynutil.insert(" ")
      + field("domain", domain)
    )
    self.fst = self.add_tokens(url | email).optimize()

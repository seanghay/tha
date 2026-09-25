import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import GraphFst, field, load_pairs
from tha.fst.itn.taggers.cardinal import CardinalFst
from tha.fst.itn.taggers.decimal import DecimalFst

# the written symbol of each spoken currency (the first one in currency.tsv)
CURRENCIES = {}
for _key, _word in load_pairs("currency.tsv"):
  CURRENCIES.setdefault(_word, _key)

# "ប្រាំចុចប្រាំលានដុល្លារ" -> "$5.5 លាន", a whole number of millions is
# written in full instead: "ប្រាំលានដុល្លារ" -> "$5,000,000"
SCALES = ["ពាន់", "ម៉ឺន", "សែន", "លាន", "ពាន់លាន", "ប៊ីលាន", "ទ្រីលាន"]


class MoneyFst(GraphFst):
  """
  មួយរយដុល្លារ          -> money { currency: "$" integer_part: "100" }
  មួយដុល្លារប្រាំសេន    -> money { currency: "$" integer_part: "1" fractional_part: "05" }
  ហាសិបសេន             -> money { currency: "$" integer_part: "0" fractional_part: "50" }
  មួយរយរៀល             -> money { currency: "៛" integer_part: "100" }
  ប្រាំចុចប្រាំលានដុល្លារ -> money { currency: "$" integer_part: "5" point: "." fractional_part: "5" scale: "លាន" }
  """

  def __init__(self, cardinal: CardinalFst, decimal: DecimalFst):
    super().__init__(name="money", kind="classify")

    words = dict(load_pairs("currency.tsv"))
    minor = {words[k]: m for k, m in load_pairs("currency_minor.tsv")}
    sp = pynutil.insert(" ")
    integer = field("integer_part", cardinal.graph_grouped)
    decimal_amount = decimal.graph
    scaled = decimal_amount + sp + field("scale", pynini.union(*SCALES))
    cents = cardinal.graph_nz @ pynini.string_map(
      [(str(n), f"{n:02d}") for n in range(1, 100)]
    )

    graphs = []
    for word, symbol in CURRENCIES.items():
      currency = field("currency", pynutil.insert(symbol)) + sp
      major = pynutil.delete(word)
      graph = integer | pynutil.add_weight(decimal_amount, 0.1) | scaled
      graph = currency + graph + major
      if word in minor:
        cents_f = sp + field("fractional_part", cents) + pynutil.delete(minor[word])
        graph |= currency + integer + major + cents_f
        graph |= currency + field("integer_part", pynutil.insert("0")) + cents_f
      graphs.append(graph)
    graph = cardinal.negative.ques + pynini.union(*graphs)
    self.fst = self.add_tokens(graph).optimize()

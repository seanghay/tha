import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import (
  GraphFst,
  delete_space_opt,
  field,
  insert_sep,
  load,
  load_pairs,
)
from tha.fst.taggers.cardinal import MINUS, CardinalFst
from tha.fst.taggers.decimal import DecimalFst


class MoneyFst(GraphFst):
  """
  Currency symbols or ISO codes before or after an amount, e.g.
    $1.05     -> money { integer_part: "មួយ" currency_maj: "ដុល្លារ"
                         fractional_part: "ប្រាំ" currency_min: "សេន" }
    100 KHR   -> money { integer_part: "មួយរយ" currency_maj: "រៀល" }
    100.32៛   -> money { amount: "មួយរយ▁ចុច▁សាមសិបពីរ" currency_maj: "រៀល" }
    $5 លាន    -> money { amount: "ប្រាំ▁លាន" currency_maj: "ដុល្លារ" }
  Only currencies listed in currency_minor.tsv are read with a minor unit.
  """

  def __init__(self, cardinal: CardinalFst, decimal: DecimalFst):
    super().__init__(name="money", kind="classify")

    minor = dict(load_pairs("currency_minor.tsv"))

    # .5 -> 50 cents, .05 -> 5 cents
    cents = pynini.string_map(
      [(f"{n:02d}", cardinal.words(n)) for n in range(1, 100)]
      + [(str(n), cardinal.words(n * 10)) for n in range(1, 10)]
    ).optimize()
    no_cents = pynini.union("0", "00")
    scales = load("money_scales.tsv")
    integer = cardinal.graph_with_grouping | pynutil.add_weight(
      cardinal.graph_grouped_dot, 0.05
    )
    non_zero_integer = pynini.difference(integer.copy().project("input"), "0") @ integer

    def sp():
      return pynutil.insert(" ")

    def body(maj: str, min_: str = None):
      maj_f = sp() + field("currency_maj", pynutil.insert(maj))
      whole = field("integer_part", integer) + maj_f
      # decimals that aren't cents: 1.999$ / 100.32៛
      amount = pynutil.add_weight(field("amount", decimal.graph_words) + maj_f, 0.1)
      # $5 លាន, $1.5M, 10K$
      scaled = (
        field(
          "amount",
          (integer | decimal.graph_words) + delete_space_opt + insert_sep + scales,
        )
        + maj_f
      )
      graph = whole | amount | scaled
      if min_:
        min_f = sp() + field("currency_min", pynutil.insert(min_))
        graph |= (
          (whole + pynutil.delete(".") + pynutil.delete(no_cents))
          | (
            field("integer_part", non_zero_integer)
            + maj_f
            + pynutil.delete(".")
            + sp()
            + field("fractional_part", cents)
            + min_f
          )
          | (pynutil.delete("0.") + field("fractional_part", cents) + min_f)
        )
      return graph

    # "$" and "USD" share one graph
    keys_by_word = {}
    for key, word in load_pairs("currency.tsv"):
      keys_by_word.setdefault((word, minor.get(key)), []).append(key)

    graphs = []
    for (word, min_), keys in keys_by_word.items():
      b = body(word, min_).optimize()
      k = pynutil.delete(pynini.union(*keys))
      graphs.append(k + delete_space_opt + b)
      graphs.append(b + delete_space_opt + k)

    optional_minus = pynini.closure(
      pynutil.insert('negative: "true" ') + pynutil.delete(MINUS), 0, 1
    )
    self.fst = self.add_tokens(optional_minus + pynini.union(*graphs)).optimize()

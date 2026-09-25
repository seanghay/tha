import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import TH_ALPHA, TH_CHAR, TH_DIGIT, TH_SIGMA, GraphFst
from tha.fst.itn.graph_utils import flexible_joins, thousands
from tha.fst.itn.taggers.arithmetic import ArithmeticFst
from tha.fst.itn.taggers.cardinal import CardinalFst
from tha.fst.itn.taggers.date import DateFst
from tha.fst.itn.taggers.decimal import DecimalFst
from tha.fst.itn.taggers.electronic import ElectronicFst
from tha.fst.itn.taggers.fraction import FractionFst
from tha.fst.itn.taggers.license_plate import LicensePlateFst
from tha.fst.itn.taggers.measure import MeasureFst
from tha.fst.itn.taggers.money import MoneyFst
from tha.fst.itn.taggers.range import RangeFst
from tha.fst.itn.taggers.serial import SerialFst
from tha.fst.itn.taggers.telephone import TelephoneFst
from tha.fst.itn.taggers.time import TimeFst

COENG = "្"
# vowel signs, diacritics and ៗ can't start a word: "ពីរោះ" isn't ពីរ + ោះ
KHMER_DEPENDENT = pynini.union(
  *[chr(c) for c in range(0x17B6, 0x17D4)], "ៗ", "៝"
).optimize()


class ClassifyFst(GraphFst):
  """
  Tags spoken text for inverse normalization, segmented like the normalizer's
  `ClassifyFst`: plain text is `name` tokens that cost 1 per character, a
  semiotic token costs a flat weight < 1, so the longest spans of number words
  win. Number words may be glued or joined with ▁ or U+200B (see
  `flexible_joins`).

  `single_digits`, `flexible`, `boundaries` and `variants` switch the design
  choices off, for measuring their effect: digits for single number words,
  flexible joins between words, the word boundary filter (`filter` accepts
  anything) and spelling variants (digit_variants.tsv).
  """

  def __init__(
    self,
    thousands_sep: str = ",",
    single_digits: bool = False,
    flexible: bool = True,
    boundaries: bool = True,
    variants: bool = True,
  ):
    super().__init__(name="tokenize_and_classify", kind="classify")

    cardinal = CardinalFst(thousands(thousands_sep), single_digits, variants)
    decimal = DecimalFst(cardinal)
    range_ = RangeFst(cardinal)
    flex = flexible_joins() if flexible else TH_SIGMA
    classes = [
      (DateFst(cardinal), 0.4, flex),
      (TimeFst(cardinal), 0.4, flex),
      (TelephoneFst(cardinal), 0.4, flex),
      (ElectronicFst(cardinal), 0.4, flex),
      (LicensePlateFst(cardinal), 0.45, flex),
      (MoneyFst(cardinal, decimal), 0.45, flex),
      (MeasureFst(cardinal, decimal, range_), 0.45, flex),
      (FractionFst(cardinal), 0.5, flex),
      (range_, 0.5, flex),
      (ArithmeticFst(cardinal), 0.5, flex),
      (cardinal, 0.5, flex),
      (decimal, 0.55, flex),
      (SerialFst(cardinal), 0.6, flex),
    ]
    self.names = [c.name for c, _, _ in classes]

    semiotic = pynini.union(
      *[pynutil.add_weight(pynini.compose(f, c.fst), w) for c, w, f in classes]
    ).optimize()
    semiotic = pynutil.insert("tokens { ") + semiotic + pynutil.insert(" }")

    quote, backslash = pynini.escape('"'), pynini.escape("\\")
    not_quote = pynini.difference(TH_CHAR, quote)
    name_char = pynini.union(
      pynini.cross(quote, backslash + quote),
      pynini.cross(backslash, backslash + backslash),
      pynini.difference(TH_CHAR, pynini.union(quote, backslash)),
    )
    name = (
      pynutil.insert('tokens { name: "')
      + pynini.closure(pynutil.add_weight(name_char, 1.0), 1)
      + pynutil.insert('" }')
    )

    sp = pynutil.insert(" ")
    graph = (
      (name + sp).ques
      + pynini.closure(semiotic + sp + name + sp)
      + (semiotic + sp).ques
    )
    self.fst = graph.optimize()

    # a token can't start or end inside a word: "ពីរោះ", "12ប្រាំ" (-> 125),
    # "hellojohn dot com"
    semiotic_start = '" } tokens { ' + pynini.union(*self.names) + " {"
    semiotic_end = '} } tokens { name: "'
    bad = pynini.union(
      COENG + semiotic_start,
      TH_DIGIT + semiotic_start + pynini.closure(not_quote) + '"' + TH_DIGIT,
      TH_ALPHA + semiotic_start + pynini.closure(not_quote) + '"' + TH_ALPHA,
      semiotic_end + KHMER_DEPENDENT,
      TH_DIGIT + '" ' + semiotic_end + TH_DIGIT,
      TH_ALPHA + '" ' + semiotic_end + TH_ALPHA,
    )
    self.filter = pynini.difference(TH_SIGMA, TH_SIGMA + bad + TH_SIGMA).optimize()
    if not boundaries:
      self.filter = TH_SIGMA

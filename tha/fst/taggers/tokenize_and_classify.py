import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import TH_ALPHA, TH_CHAR, TH_DIGIT, TH_SIGMA, GraphFst, load
from tha.fst.taggers.cardinal import CardinalFst
from tha.fst.taggers.code import CodeFst
from tha.fst.taggers.date import DateFst
from tha.fst.taggers.decimal import DecimalFst
from tha.fst.taggers.electronic import ElectronicFst
from tha.fst.taggers.formation import FormationFst
from tha.fst.taggers.fraction import FractionFst
from tha.fst.taggers.license_plate import LicensePlateFst
from tha.fst.taggers.measure import MeasureFst
from tha.fst.taggers.money import MoneyFst
from tha.fst.taggers.ordinal import OrdinalFst
from tha.fst.taggers.roman import RomanFst
from tha.fst.taggers.serial import SerialFst
from tha.fst.taggers.telephone import TelephoneFst
from tha.fst.taggers.time import TimeFst
from tha.fst.taggers.whitelist import WhiteListFst
from tha.fst.taggers.year_range import YearRangeFst

SCALE_WORDS = ["ពាន់", "ម៉ឺន", "សែន", "លាន", "ប៊ីលាន", "ទ្រីលាន"]

# classes that must not touch a latin letter on their left / right side,
# e.g. "x1st", "1stly", "5 mango" (5 m + ango), "10:23am-ish"
LEFT_BOUNDED = [
  "ordinal",
  "time",
  "date",
  "telephone",
  "electronic",
  "license_plate",
  "code",
  "year_range",
  "formation",
]
RIGHT_BOUNDED = LEFT_BOUNDED + ["measure", "money", "serial", "roman", "fraction"]


class ClassifyFst(GraphFst):
  """
  Tags a whole piece of text. Khmer isn't written with spaces between words,
  so instead of classifying whitespace separated tokens (like NeMo does) the
  text is segmented here: plain text becomes `name` tokens that cost 1 per
  character, a semiotic token costs a flat weight < 1, so the cheapest path
  prefers the fewest and longest semiotic tokens. Digits are never allowed in
  `name` tokens, which guarantees every digit gets verbalized.

  Tokens alternate between `name` and semiotic ones, two semiotic tokens are
  never adjacent (that would split "10:234" into a time and a cardinal).
  """

  def __init__(self):
    super().__init__(name="tokenize_and_classify", kind="classify")

    cardinal = CardinalFst()
    decimal = DecimalFst(cardinal)
    classes = [
      (WhiteListFst(), 0.3),
      (DateFst(cardinal), 0.4),
      (YearRangeFst(cardinal), 0.4),
      (FormationFst(cardinal), 0.4),
      (TimeFst(cardinal), 0.4),
      (TelephoneFst(cardinal), 0.4),
      (ElectronicFst(cardinal), 0.4),
      (LicensePlateFst(cardinal), 0.45),
      (MoneyFst(cardinal, decimal), 0.45),
      (MeasureFst(cardinal, decimal), 0.45),
      (OrdinalFst(cardinal), 0.45),
      (RomanFst(cardinal), 0.45),
      (FractionFst(cardinal), 0.5),
      (cardinal, 0.5),
      (decimal, 0.55),
      (SerialFst(cardinal), 0.6),
      (CodeFst(cardinal), 0.55),
    ]

    semiotic = pynini.union(
      *[pynutil.add_weight(c.fst, w) for c, w in classes]
    ).optimize()
    semiotic = pynutil.insert("tokens { ") + semiotic + pynutil.insert(" }")

    # `"` and `\` are escaped inside the quoted value (pynini strings treat a
    # backslash as an escape char too, hence pynini.escape)
    quote, backslash = pynini.escape('"'), pynini.escape("\\")
    # symbols that are pronounced (symbols.tsv) are spoken inside plain text
    # too, so they never reach a TTS/ASR transcript raw
    # ½ on its own (e.g. glued to other digits) is spoken like a fraction
    vulgar = load("fractions.tsv") @ (
      cardinal.graph + pynini.cross("/", "ភាគ") + cardinal.graph
    )
    symbols = pynini.union(load("symbols.tsv"), vulgar).optimize()
    name_char = pynini.union(
      pynini.cross(quote, backslash + quote),
      pynini.cross(backslash, backslash + backslash),
      symbols,
      pynini.difference(
        TH_CHAR,
        pynini.union(quote, backslash, TH_DIGIT, symbols.copy().project("input")),
      ),
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

    # boundary constraints, applied on the tagged lattice
    left = pynini.union(*LEFT_BOUNDED)
    right = pynini.union(*RIGHT_BOUNDED)
    not_brace = pynini.difference(TH_CHAR, "}")
    bad = pynini.union(
      TH_ALPHA + '" } tokens { ' + left + " {",
      "tokens { "
      + right
      + " {"
      + pynini.closure(not_brace)
      + '} } tokens { name: "'
      + TH_ALPHA,
      # ២.១៦៦លាន is 2.166 million: no dot thousands before a scale word
      'grouping: "dot" } } tokens { name: "'
      + pynini.closure(" ", 0, 1)
      + pynini.union(*SCALE_WORDS),
    )
    self.filter = pynini.difference(TH_SIGMA, TH_SIGMA + bad + TH_SIGMA).optimize()

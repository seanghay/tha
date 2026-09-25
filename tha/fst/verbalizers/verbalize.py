import pynini

from tha.fst.graph_utils import GraphFst
from tha.fst.verbalizers.cardinal import CardinalFst
from tha.fst.verbalizers.date import DateFst
from tha.fst.verbalizers.decimal import DecimalFst
from tha.fst.verbalizers.electronic import ElectronicFst
from tha.fst.verbalizers.fraction import FractionFst
from tha.fst.verbalizers.measure import MeasureFst
from tha.fst.verbalizers.money import MoneyFst
from tha.fst.verbalizers.ordinal import OrdinalFst
from tha.fst.verbalizers.roman import RomanFst
from tha.fst.verbalizers.simple import SingleFieldFst
from tha.fst.verbalizers.time import TimeFst
from tha.fst.verbalizers.year_range import YearRangeFst


class VerbalizeFst(GraphFst):
  """Verbalizes a single semiotic token, e.g. `cardinal { integer: "ប្រាំ" }`."""

  def __init__(self):
    super().__init__(name="verbalize", kind="verbalize")
    verbalizers = [
      CardinalFst(),
      DecimalFst(),
      OrdinalFst(),
      FractionFst(),
      RomanFst(),
      MoneyFst(),
      MeasureFst(),
      TimeFst(),
      DateFst(),
      ElectronicFst(),
      SingleFieldFst("serial", "value"),
      SingleFieldFst("telephone", "number_part"),
      SingleFieldFst("license_plate", "value"),
      SingleFieldFst("whitelist", "value"),
      SingleFieldFst("code", "value"),
      SingleFieldFst("formation", "value"),
      YearRangeFst(),
    ]
    self.fst = pynini.union(*[v.fst for v in verbalizers]).optimize()

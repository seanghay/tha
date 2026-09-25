import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import TH_QUOTE_FREE, GraphFst, delete_field, delete_space
from tha.fst.itn.taggers.money import CURRENCIES

# currencies written before the amount, the others go after it: 100៛
PREFIX_CURRENCIES = {"$", "€", "£", "¥", "₩"}
# units glued to the number: 50%, 30°C
GLUED_UNITS = {"%", "٪", "％", "°C", "℃", "°F", "°"}


def _join(*parts):
  """Concatenates verbalizer parts, deleting the spaces between fields."""
  out = parts[0]
  for p in parts[1:]:
    out = out + delete_space + p
  return out


def _negative():
  """negative: "-" -> -, before anything else of the token"""
  return (delete_field("negative") + delete_space).ques


def _number():
  """integer_part [point fractional_part] -> 12.5, cents use "." too"""
  point = delete_field("point") | pynutil.insert(".")
  return (
    delete_field("integer_part")
    + (delete_space + point + delete_space + delete_field("fractional_part")).ques
  )


class CardinalFst(GraphFst):
  """cardinal { prefix: "ទី" integer: "3" } -> ទី3"""

  def __init__(self):
    super().__init__(name="cardinal", kind="verbalize")
    graph = (delete_field("prefix") + delete_space).ques + delete_field("integer")
    graph |= _negative() + delete_field("integer")
    self.fst = self.delete_tokens(graph).optimize()


class DecimalFst(GraphFst):
  """decimal { integer_part: "12" point: "." fractional_part: "5" } -> 12.5"""

  def __init__(self):
    super().__init__(name="decimal", kind="verbalize")
    self.fst = self.delete_tokens(_negative() + _number()).optimize()


class MoneyFst(GraphFst):
  """money { currency: "$" integer_part: "1" fractional_part: "05" } -> $1.05
  money { currency: "៛" integer_part: "100" } -> 100៛"""

  def __init__(self):
    super().__init__(name="money", kind="verbalize")
    scale = (delete_space + pynutil.insert(" ") + delete_field("scale")).ques
    amount = _number() + scale
    graphs = []
    for symbol in set(CURRENCIES.values()):
      currency = pynutil.delete(f'currency: "{symbol}"') + delete_space
      if symbol in PREFIX_CURRENCIES:
        graphs.append(currency + pynutil.insert(symbol) + amount)
      else:
        graphs.append(currency + amount + pynutil.insert(symbol))
    self.fst = self.delete_tokens(_negative() + pynini.union(*graphs)).optimize()


class MeasureFst(GraphFst):
  """measure { integer_part: "5" units: "km" } -> 5 km"""

  def __init__(self):
    super().__init__(name="measure", kind="verbalize")
    glued = pynini.union(*GLUED_UNITS)
    spaced = pynini.difference(pynini.closure(TH_QUOTE_FREE, 1), glued)
    units = delete_field("units", glued) | (
      pynutil.insert(" ") + delete_field("units", spaced)
    )
    self.fst = self.delete_tokens(_negative() + _join(_number(), units)).optimize()


class TimeFst(GraphFst):
  """time { hours: "8" minutes: "30" } -> 8:30"""

  def __init__(self):
    super().__init__(name="time", kind="verbalize")
    colon = pynutil.insert(":")
    graph = _join(delete_field("hours") + colon, delete_field("minutes"))
    graph += (delete_space + colon + delete_field("seconds")).ques
    self.fst = self.delete_tokens(graph).optimize()


class DateFst(GraphFst):
  """date { day: "02" month: "01" year: "2024" } -> 02/01/2024"""

  def __init__(self):
    super().__init__(name="date", kind="verbalize")
    slash = pynutil.insert("/")
    graph = _join(
      delete_field("day") + slash,
      delete_field("month") + slash,
      delete_field("year"),
    )
    self.fst = self.delete_tokens(graph).optimize()


class FractionFst(GraphFst):
  """fraction { integer_part: "1" numerator: "1" denominator: "2" } -> 1 1/2"""

  def __init__(self):
    super().__init__(name="fraction", kind="verbalize")
    integer = delete_field("integer_part") + delete_space + pynutil.insert(" ")
    graph = integer.ques + _join(
      delete_field("numerator") + pynutil.insert("/"), delete_field("denominator")
    )
    self.fst = self.delete_tokens(graph).optimize()


class SingleFieldFst(GraphFst):
  def __init__(self, name: str, key: str):
    super().__init__(name=name, kind="verbalize")
    self.fst = self.delete_tokens(delete_field(key)).optimize()


class VerbalizeFst(GraphFst):
  """Writes a single tagged token, e.g. `cardinal { integer: "5" }` -> 5."""

  def __init__(self):
    super().__init__(name="verbalize", kind="verbalize")
    verbalizers = [
      CardinalFst(),
      DecimalFst(),
      MoneyFst(),
      MeasureFst(),
      TimeFst(),
      DateFst(),
      FractionFst(),
      SingleFieldFst("telephone", "number_part"),
      SingleFieldFst("electronic", "value"),
      SingleFieldFst("license_plate", "value"),
      SingleFieldFst("serial", "value"),
      SingleFieldFst("range", "value"),
      SingleFieldFst("arithmetic", "value"),
    ]
    self.fst = pynini.union(*[v.fst for v in verbalizers]).optimize()

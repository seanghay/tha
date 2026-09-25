import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import TH_DIGIT, GraphFst, field, insert_sep, load
from tha.fst.taggers.cardinal import CardinalFst


def spelled_letters(max_letters: int) -> pynini.Fst:
  """AB -> អេ▁ប៊ី, uppercase latin letters spelled with their Khmer names"""
  letter = load("latin_letters.tsv")
  return (letter + pynini.closure(insert_sep + letter, 0, max_letters - 1)).optimize()


class CodeFst(GraphFst):
  """
  Short codes of uppercase latin letters glued to a number, letters are
  spelled (latin_letters.tsv) and the number is read as a number:
    U19   -> code { value: "យូ▁ដប់ប្រាំបួន" }
    F-35  -> code { value: "អេហ្វ▁សាមសិបប្រាំ" }
    MH370 -> code { value: "អឹម▁អេច▁បីរយ▁ចិតសិប" }
    5G    -> code { value: "ប្រាំ▁ជី" }
  Units (5V, 5GB) and money (10K$) are matched by their own classes first.
  """

  def __init__(self, cardinal: CardinalFst):
    super().__init__(name="code", kind="classify")
    letters = spelled_letters(3)
    number = pynini.closure(TH_DIGIT, 1, 4) @ cardinal.graph_any
    letters_first = letters + pynutil.delete("-").ques + insert_sep + number
    number_first = number + insert_sep + spelled_letters(2)
    self.fst = self.add_tokens(field("value", letters_first | number_first)).optimize()

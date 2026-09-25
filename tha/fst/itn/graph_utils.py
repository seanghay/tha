import pynini
from pynini.lib import pynutil

from tha.fst.graph_utils import (
  SEP,
  TH_CHAR,
  TH_DIGIT,
  TH_NON_ZERO,
  TH_SIGMA,
)

# Khmer is written without spaces between words, a space marks a phrase
# boundary. Number words are glued ("មួយរយម្ភៃ") or joined with the
# normalizer's separator or a zero width space ("មួយរយ▁ម្ភៃ")
JOINERS = pynini.union(SEP, "\u200b").optimize()


def _between(tau: pynini.Fst, left: pynini.Fst, right: pynini.Fst) -> pynini.Fst:
  return pynini.cdrewrite(tau, left, right, TH_SIGMA, mode="opt").optimize()


def flexible_joins() -> pynini.Fst:
  """
  Optionally deletes a joiner (▁ or U+200B) between two characters of the
  input, so that the grammars are written without them. Composed on the input
  side of a class: `flexible_joins() @ graph`. The ends of a token keep their
  joiners, those are part of the surrounding text. Spaces are kept: in Khmer
  they separate phrases, not words.
  """
  return _between(pynutil.delete(JOINERS), TH_CHAR, TH_CHAR)


def thousands(sep: str) -> pynini.Fst:
  """1234567 -> 1,234,567, numbers of four digits and less are left alone
  (years: 2024)."""
  if not sep:
    return pynini.closure(TH_DIGIT, 1).optimize()
  grouped = (
    TH_NON_ZERO
    + pynini.closure(TH_DIGIT, 0, 2)
    + pynini.closure(pynutil.insert(sep) + TH_DIGIT**3, 1)
  )
  long = TH_NON_ZERO + pynini.closure(TH_DIGIT, 4)
  short = pynini.closure(TH_DIGIT, 1, 4)
  return ((long @ grouped) | short).optimize()

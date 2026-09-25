import functools

import pynini
import regex as re
from pynini.lib import rewrite

from tha.fst.graph_utils import SEP
from tha.fst.itn.taggers.tokenize_and_classify import ClassifyFst
from tha.fst.itn.verbalizers.verbalize import VerbalizeFst
from tha.fst.normalizer import TokenParser

KHMER_DIGITS = str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩")
# "9:05▁យប់": a separator left between a written token and a word
RE_SEP_START = re.compile(f"^{SEP}+")
RE_SEP_END = re.compile(f"{SEP}+$")
# "ក្មេង▁ក្មេង" -> "ក្មេងៗ", the normalizer expands the repetition mark so
RE_REPEATED = re.compile(
  r"([\u1780-\u17b3][\u1780-\u17d3\u17dd]*)" + SEP + r"\1(?![\u17b6-\u17d3\u17dd])"
)


@functools.cache
def _grammars(thousands_sep: str):
  classify = ClassifyFst(thousands_sep)
  return classify.fst, classify.filter, VerbalizeFst().fst


class InverseNormalizer:
  """
  Khmer inverse text normalization: spoken numbers, money, measures, times,
  dates, phone numbers, e-mails, ... back to their written form, the inverse
  of `Normalizer`.

    >>> InverseNormalizer().inverse_normalize("តម្លៃ មួយ▁ដុល្លារ▁ប្រាំ▁សេន")
    'តម្លៃ $1.05'
    >>> InverseNormalizer().inverse_normalize("ទិញពីររយហាសិបគីឡូក្រាម")
    'ទិញ250 kg'

  Number words may be glued or joined with ▁ or U+200B ("ពីររយ▁ហាសិប"), a
  space is a boundary as in any Khmer text.
  Words repeated with ▁ get their repetition mark back: "ក្មេង▁ក្មេង" -> "ក្មេងៗ".
  Single digits on their own stay words ("មួយចំនួន"), except after ទី and
  លេខ ("ទីបី" -> "ទី3").

  `thousands_sep` groups numbers of five digits and more ("10,000"), "" to
  not group them. `khmer_digits` writes ០១២... instead of 012...
  """

  def __init__(self, thousands_sep: str = ",", khmer_digits: bool = False):
    self.khmer_digits = khmer_digits
    self.tagger, self.filter, self.verbalizer = _grammars(thousands_sep)

  def tag(self, text: str) -> str:
    """Tagged form of a single line of text."""
    if not text:
      return ""
    lattice = pynini.compose(pynini.escape(text), self.tagger)
    lattice = pynini.compose(lattice.project("output"), self.filter)
    return pynini.shortestpath(lattice).string().strip()

  def verbalize_token(self, name: str, fields) -> str:
    serialized = f"{name} {{ " + " ".join(f'{k}: "{v}"' for k, v in fields) + " }"
    out = rewrite.top_rewrite(pynini.escape(serialized), self.verbalizer)
    return out.translate(KHMER_DIGITS) if self.khmer_digits else out

  def verbalize(self, tagged: str) -> str:
    tokens = TokenParser(tagged).parse()
    out = []
    for i, (name, value) in enumerate(tokens):
      if name != "name":
        out.append(self.verbalize_token(name, value))
        continue
      value = RE_REPEATED.sub(r"\1ៗ", value)
      if i > 0:
        value = RE_SEP_START.sub(" ", value)
      if i + 1 < len(tokens):
        value = RE_SEP_END.sub(" ", value)
      out.append(value)
    return "".join(out)

  def inverse_normalize(self, text: str) -> str:
    return "\n".join(self.verbalize(self.tag(line)) for line in text.split("\n"))


_default = None


def inverse_normalize_text(text: str) -> str:
  """Inverse normalizes text with a shared `InverseNormalizer`."""
  global _default
  if _default is None:
    _default = InverseNormalizer()
  return _default.inverse_normalize(text)


__all__ = ["InverseNormalizer", "inverse_normalize_text"]

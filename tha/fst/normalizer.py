import functools

import pynini
import regex as re
from pynini.lib import rewrite

from tha import repeater
from tha.fst.graph_utils import (
  SEP,
  TH_ALNUM,
  TH_CHAR,
  TH_DIGIT,
  TH_KHMER,
  TH_SIGMA,
  TH_SPACE,
  load_pairs,
)
from tha.fst.taggers.cardinal import MINUS
from tha.fst.taggers.tokenize_and_classify import ClassifyFst
from tha.fst.verbalizers.verbalize import VerbalizeFst

KHMER_DIGITS = str.maketrans("០១២៣៤៥៦៧៨៩", "0123456789")

# the verbalizers expect the fields of these classes in this order
FIELD_ORDER = {
  "date": ["day", "month", "year"],
}

RE_REPEATED_SEP = re.compile(f"{SEP}+")
# "កូវីដ-១៩", "5-star", "១-ដំណាក់": a hyphen between a word and a number is
# spoken as a pause, unlike "2-3" (a range) or "-5" (minus)
RE_LETTER_HYPHEN_END = re.compile(r"(?<=[A-Za-z\u1780-\u17d3\u17dd])-$")
RE_LETTER_HYPHEN_START = re.compile(r"^-(?=[A-Za-z\u1780-\u17d3\u17dd])")

# "2-3", "8:00-17:00", "5-10%": a dash on its own between two quantities is a
# range, spoken "ដល់"
RANGE_WORD = "ដល់"
# ... but a score in a line about sports: "ឈ្នះ ១-០" -> "មួយ▁ទល់▁សូន្យ"
SCORE_WORD = "ទល់"
SCORE_CONTEXT = [w for (w,) in load_pairs("score_context.tsv")]
# still a range right after these words: "ថ្ងៃទី ៥-៧"
RE_RANGE_CONTEXT = re.compile(
  "(?:" + "|".join(w for (w,) in load_pairs("range_context.tsv")) + r")\s*$"
)
RE_RANGE_DASH = re.compile(r"^(\s*)[-–—](\s*)$")
RE_LATIN_END = re.compile(r"[A-Za-z]\s+$")
RE_LATIN_START = re.compile(r"^\s+[A-Z]")
# "5x20 ម៉ែត្រ", "4 X 6"
TIMES_WORD = "គុណ"
RE_TIMES = re.compile(r"^(\s*)[xX](\s*)$")
TIMES_CLASSES = {"cardinal", "decimal", "measure", "fraction"}
RANGE_CLASSES = {
  "cardinal",
  "decimal",
  "ordinal",
  "fraction",
  "money",
  "measure",
  "time",
  "date",
}


class TokenParser:
  """Parses the tagger output, e.g.
  `tokens { name: "ឆ្នាំ" } tokens { cardinal { integer: "..." } }`
  into [("name", "ឆ្នាំ"), ("cardinal", [("integer", "...")])]
  """

  def __init__(self, text: str):
    self.text = text
    self.i = 0

  def _expect(self, s: str):
    if not self.text.startswith(s, self.i):
      raise ValueError(
        f"expected {s!r} at {self.i}: {self.text[self.i : self.i + 40]!r}"
      )
    self.i += len(s)

  def _until(self, s: str) -> str:
    j = self.text.index(s, self.i)
    out = self.text[self.i : j]
    self.i = j + len(s)
    return out

  def _quoted(self) -> str:
    out = []
    while True:
      c = self.text[self.i]
      if c == "\\":
        out.append(self.text[self.i + 1])
        self.i += 2
      elif c == '"':
        self.i += 1
        return "".join(out)
      else:
        out.append(c)
        self.i += 1

  def parse(self):
    tokens = []
    while True:
      while self.text.startswith(" ", self.i):
        self.i += 1
      if self.i >= len(self.text):
        return tokens
      self._expect("tokens { ")
      if self.text.startswith('name: "', self.i):
        self.i += len('name: "')
        tokens.append(("name", self._quoted()))
        self._expect(" }")
        continue
      name = self._until(" { ")
      fields = []
      while not self.text.startswith("} }", self.i):
        key = self._until(': "')
        fields.append((key, self._quoted()))
        self._expect(" ")
      self._expect("} }")
      tokens.append((name, fields))


@functools.lru_cache(maxsize=None)
def _base_grammars():
  """Compiled grammars, shared by all Normalizers of the process (they take a
  few seconds to build)."""
  classify = ClassifyFst()
  verbalizer = VerbalizeFst().fst

  # a hyphen is a minus sign only when it isn't glued to a word or number
  # on its left, "-5" / "(-5)" but not "2-3" or "COVID-19"
  currency = pynini.union(*[k for k, _ in load_pairs("currency.tsv") if len(k) == 1])
  left = pynini.union(
    "[BOS]",
    pynini.difference(TH_CHAR, pynini.union(TH_ALNUM, TH_KHMER, ".", ",", "-", MINUS)),
  )
  right = TH_DIGIT | (currency + TH_SPACE.ques + TH_DIGIT)
  minus = pynini.cdrewrite(pynini.cross("-", MINUS), left, right, TH_SIGMA).optimize()
  return classify.fst, classify.filter, verbalizer, minus


@functools.lru_cache(maxsize=None)
def _grammars(dot_thousands: bool):
  tagger, filter_, verbalizer, minus = _base_grammars()
  if not dot_thousands:
    no_dot = pynini.difference(TH_SIGMA, TH_SIGMA + 'grouping: "dot"' + TH_SIGMA)
    filter_ = pynini.intersect(filter_, no_dot.optimize()).optimize()
  return tagger, filter_, verbalizer, minus


class Normalizer:
  """
  Khmer text normalization with weighted finite-state transducers, similar to
  NeMo's text processing: the text is tagged into semiotic tokens (cardinal,
  money, time, ...) and every token is then verbalized.

    >>> Normalizer().normalize("តម្លៃ $1.05")
    'តម្លៃ មួយ▁ដុល្លារ▁ប្រាំ▁សេន'

  `separator` joins the spoken parts of a single token (the words of a
  number, a number and its unit, ...), e.g. "" or " " for transcripts that
  shouldn't contain "▁".

  `word_tokenizer`: segments Khmer words to expand the repetition mark ៗ
  ("ក្មេងៗ" -> "ក្មេង▁ក្មេង"), `khmercut.nn.tokenize` by default. Pass False to
  leave ៗ in the text.

  `dot_thousands`: read 1.000 as one thousand (the usual meaning in Khmer
  text) instead of a decimal. `scores`: read N-N as a score ("ទល់") in lines
  about sports instead of always as a range ("ដល់").
  """

  def __init__(
    self,
    separator: str = SEP,
    dot_thousands: bool = True,
    scores: bool = True,
    word_tokenizer=None,
  ):
    self.separator = separator
    self.word_tokenizer = word_tokenizer
    self.scores = scores
    self.tagger, self.filter, self.verbalizer, self.minus = _grammars(dot_thousands)

  def _tokenizer(self):
    if self.word_tokenizer is None:
      from khmercut import nn

      self.word_tokenizer = nn.tokenize
    return self.word_tokenizer

  def preprocess(self, text: str) -> str:
    if "ៗ" in text and self.word_tokenizer is not False:
      text = repeater.processor(text, tokenizer=self._tokenizer(), sep=self.separator)
    text = text.translate(KHMER_DIGITS)
    if "-" in text:
      text = rewrite.top_rewrite(pynini.escape(text), self.minus)
    return text

  def tag(self, text: str) -> str:
    """Tagged form of a single line of text."""
    text = self.preprocess(text)
    if not text:
      return ""
    lattice = pynini.compose(pynini.escape(text), self.tagger)
    lattice = pynini.compose(lattice.project("output"), self.filter)
    return pynini.shortestpath(lattice).string().strip()

  def verbalize_token(self, name: str, fields) -> str:
    order = FIELD_ORDER.get(name)
    if order:
      fields = sorted(fields, key=lambda f: order.index(f[0]))
    serialized = f"{name} {{ " + " ".join(f'{k}: "{v}"' for k, v in fields) + " }"
    out = rewrite.top_rewrite(pynini.escape(serialized), self.verbalizer)
    out = RE_REPEATED_SEP.sub(SEP, out).strip(SEP)
    return out.replace(SEP, self.separator)

  def _between(self, tokens, i, classes) -> bool:
    return (
      0 < i < len(tokens) - 1
      and tokens[i - 1][0] in classes
      and tokens[i + 1][0] in classes
    )

  def verbalize(self, tagged: str) -> str:
    tokens = TokenParser(tagged).parse()
    text = "".join(v for n, v in tokens if n == "name")
    sports = self.scores and any(w in text for w in SCORE_CONTEXT)
    out = []
    for i, (name, value) in enumerate(tokens):
      if name != "name":
        out.append(self.verbalize_token(name, value))
        continue
      # names and semiotic tokens alternate, so a neighbour is always semiotic
      m = RE_RANGE_DASH.match(value)
      if (
        m
        and self._between(tokens, i, RANGE_CLASSES)
        # 2024-13-40 is a chain, not a range
        and not (i >= 2 and RE_RANGE_DASH.match(tokens[i - 2][1]))
        and not (i + 2 < len(tokens) and RE_RANGE_DASH.match(tokens[i + 2][1]))
      ):
        before = tokens[i - 2][1] if i >= 2 else ""
        after = tokens[i + 2][1] if i + 2 < len(tokens) else ""
        # "France 0-0 Uruguay": team names on both sides
        teams = bool(RE_LATIN_END.search(before) and RE_LATIN_START.match(after))
        score = (
          self.scores
          and (sports or teams)
          and tokens[i - 1][0] == tokens[i + 1][0] == "cardinal"
          and not RE_RANGE_CONTEXT.search(before)
        )
        word = SCORE_WORD if score else RANGE_WORD
        out.append((m[1] or self.separator) + word + (m[2] or self.separator))
        continue
      m = RE_TIMES.match(value)
      if m and self._between(tokens, i, TIMES_CLASSES):
        out.append((m[1] or self.separator) + TIMES_WORD + (m[2] or self.separator))
        continue
      if i + 1 < len(tokens):
        value = RE_LETTER_HYPHEN_END.sub(self.separator, value)
      if i > 0:
        value = RE_LETTER_HYPHEN_START.sub(self.separator, value)
      out.append(value)
    return "".join(out)

  def normalize(self, text: str) -> str:
    return "\n".join(self.verbalize(self.tag(line)) for line in text.split("\n"))


_default = None


def normalize_text(text: str) -> str:
  """Normalizes text with a shared `Normalizer` (built on first use)."""
  global _default
  if _default is None:
    _default = Normalizer()
  return _default.normalize(text)


__all__ = ["Normalizer", "TokenParser", "normalize_text"]

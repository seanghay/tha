import os

import pynini
from pynini.lib import pynutil, utf8

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# separator inserted between the spoken parts of a single semiotic token
SEP = "▁"

TH_CHAR = utf8.VALID_UTF8_CHAR
TH_SIGMA = pynini.closure(TH_CHAR).optimize()
TH_DIGIT = pynini.union(*"0123456789").optimize()
TH_NON_ZERO = pynini.union(*"123456789").optimize()
TH_LOWER = pynini.union(*"abcdefghijklmnopqrstuvwxyz").optimize()
TH_UPPER = pynini.union(*"ABCDEFGHIJKLMNOPQRSTUVWXYZ").optimize()
TH_ALPHA = pynini.union(TH_LOWER, TH_UPPER).optimize()
TH_ALNUM = pynini.union(TH_ALPHA, TH_DIGIT).optimize()
TH_SPACE = pynini.union(" ", "\t").optimize()
TH_KHMER = pynini.union(*[chr(c) for c in range(0x1780, 0x17DE)]).optimize()

insert_sep = pynutil.insert(SEP)
delete_space = pynini.closure(pynutil.delete(TH_SPACE))
delete_space_opt = pynutil.delete(TH_SPACE).ques

# chars that may not appear inside a quoted field value unescaped
TH_QUOTE_FREE = pynini.difference(
  TH_CHAR, pynini.union('"', pynini.escape("\\"))
).optimize()


def load(name: str) -> pynini.Fst:
  """Load a two-column TSV from data/ as a string map."""
  return pynini.string_file(os.path.join(DATA_DIR, name)).optimize()


def load_pairs(name: str):
  with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
    return [tuple(line.rstrip("\n").split("\t")) for line in f if line.strip()]


def field(key: str, value: pynini.Fst) -> pynini.Fst:
  """Wraps a graph in `key: "..."` of the tagged representation."""
  return pynutil.insert(f'{key}: "') + value + pynutil.insert('"')


def delete_field(key: str, value: pynini.Fst = None) -> pynini.Fst:
  """Inverse of `field` for the verbalizers, keeping the (possibly mapped) value."""
  value = pynini.closure(TH_QUOTE_FREE, 1) if value is None else value
  return pynutil.delete(f'{key}: "') + value + pynutil.delete('"')


class GraphFst:
  """Base class of every tagger/verbalizer, mirrors NeMo's GraphFst."""

  def __init__(self, name: str, kind: str):
    self.name = name
    self.kind = kind
    self.fst = None

  def add_tokens(self, fst: pynini.Fst) -> pynini.Fst:
    """`name { ... }` around a tagger graph."""
    return pynutil.insert(f"{self.name} {{ ") + fst + pynutil.insert(" }")

  def delete_tokens(self, fst: pynini.Fst) -> pynini.Fst:
    """Strips `name { ... }` in a verbalizer graph."""
    return (
      pynutil.delete(f"{self.name} {{")
      + delete_space
      + fst
      + delete_space
      + pynutil.delete("}")
    )

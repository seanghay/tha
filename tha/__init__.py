"""Khmer text normalization and verbalization.

>>> import tha
>>> tha.normalize_text("តម្លៃ $1.05")
'តម្លៃ មួយ▁ដុល្លារ▁ប្រាំ▁សេន'
>>> tha.inverse_normalize_text("តម្លៃ មួយ▁ដុល្លារ▁ប្រាំ▁សេន")
'តម្លៃ $1.05'
"""

_MODULES = {
  "Normalizer": "tha.fst.normalizer",
  "normalize_text": "tha.fst.normalizer",
  "InverseNormalizer": "tha.fst.itn.inverse_normalizer",
  "inverse_normalize_text": "tha.fst.itn.inverse_normalizer",
}

__all__ = list(_MODULES)


def __getattr__(name):
  # the grammars pull in pynini, only load them when they're used
  if name in _MODULES:
    import importlib

    return getattr(importlib.import_module(_MODULES[name]), name)
  raise AttributeError(f"module 'tha' has no attribute {name!r}")

# -*- coding: utf-8 -*-
import regex as re
from tha.strings import overwrite_spans

RE_ONLY_TIME = re.compile(
  r"([0-9\u17e0-\u17e9]{1,2}):([0-9\u17e0-\u17e9]{2})\s?(am|pm|AM|PM)?"
)

RE_DATE_YEAR_FIRST = re.compile(
  r"([\u17e0-\u17e9\d]{4})([/-])([\u17e0-\u17e9\d]{2})\2([\u17e0-\u17e9\d]{2})"
)

RE_DATE_DAY_FIRST = re.compile(
  r"([\u17e0-\u17e9\d]{2})([/-])([\u17e0-\u17e9\d]{2})\2([\u17e0-\u17e9\d]{4})"
)


def date_processor(text: str) -> str:
  replacements = []

  for m in RE_DATE_YEAR_FIRST.finditer(text):
    replacement = f"{m[1]} {m[3]} {m[4]}"
    replacements.append((m.start(), m.end(), replacement))

  for m in RE_DATE_DAY_FIRST.finditer(text):
    replacement = f"{m[1]} {m[3]} {m[4]}"
    replacements.append((m.start(), m.end(), replacement))

  return overwrite_spans(text, replacements)


def time_processor(text: str) -> str:
  replacements = []
  for m in RE_ONLY_TIME.finditer(text):
    replacement = f"{m[1]} {m[2]}"
    if m[3] is not None:
      replacement += "▁" + "▁".join(m[3])
    replacements.append((m.start(), m.end(), replacement))
  return overwrite_spans(text, replacements)

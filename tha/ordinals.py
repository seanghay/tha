import regex as re
from tha.cardinals import processor as cardinals_processor

RE_ORDINALS = re.compile(r"([0-9]+)(st|nd|rd|th)")


def processor(text: str, **kwargs) -> str:
  if not RE_ORDINALS.search(text):
    return text
  return cardinals_processor(RE_ORDINALS.sub(r"ទី▁\1", text), **kwargs)

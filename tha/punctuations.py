import regex as re

RE_ENCLOSED_QUOUTING = re.compile(r'«[^»]+» *[។៕]?|"[^"]+" *[។៕]?|“[^”]+” *[។៕]?')


def processor(text: str):
  offset = 0
  for m in RE_ENCLOSED_QUOUTING.finditer(text):
    yield text[offset : m.start()]
    yield text[m.start() : m.end()]
    offset = m.end()
  if offset < len(text):
    yield text[offset:]

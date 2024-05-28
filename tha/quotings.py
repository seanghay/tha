import regex as re

RE_SYMBOLS = re.compile(r"[ ]*[៖«»“”\"`\u2018\u2019]+[ ]*")


def processor(text: str) -> str:
  return RE_SYMBOLS.sub(" ", text)

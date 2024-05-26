import regex as re

RE_LINES = re.compile(r"([\-_=\.,#*])\1{2,}")


def processor(text: str, repl="") -> str:
  return RE_LINES.sub(repl, text)

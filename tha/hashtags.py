import regex as re

RE_HASH_TAGS = re.compile(r"\#[A-Za-z0-9\u1780-\u17ff_]+")


def processor(text: str, repl="") -> str:
  return RE_HASH_TAGS.sub(repl, text)

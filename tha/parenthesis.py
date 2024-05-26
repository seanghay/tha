import regex as re

RE_ENCLOSED_PARENT = re.compile(r"\s*\((.*?)\)\s*|\s*\[(.*?)\]\s*")

def processor(text: str) -> str:
  return RE_ENCLOSED_PARENT.sub(" ", text)
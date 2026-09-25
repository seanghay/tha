import regex as re

# balanced, possibly nested (...) or [...]
RE_ENCLOSED_PARENT = re.compile(
  r"\s*(?:(\((?:[^()]++|(?1))*\))|(\[(?:[^\[\]]++|(?2))*\]))\s*"
)


def processor(text: str) -> str:
  def replacer(m):
    # don't leave dangling spaces at the start/end of the text
    if m.start() == 0 or m.end() == len(text):
      return ""
    return " "

  return RE_ENCLOSED_PARENT.sub(replacer, text)

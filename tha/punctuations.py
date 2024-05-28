import regex as re

SENTENCE_SEPARATOR = ["។", "៕", "?", "!"]
RE_SENTENCE_SEPARATOR = re.compile("(?<=[" + "".join(SENTENCE_SEPARATOR) + "])")
RE_REPEATING_PUNCT = re.compile(r"([?!៕។៖]){2,}")

def split_on_punctuations(text: str):
  values = RE_SENTENCE_SEPARATOR.split(text)
  if values[-1]:
    return values
  return values[:-1]

def processor(text: str):
  sentences = []
  for line in text.splitlines():
    line = line.strip()
    if not line:
      continue
    line = RE_REPEATING_PUNCT.sub(r"\1", line)
    for sentence in split_on_punctuations(line):
      sentences.append(sentence)
  return sentences


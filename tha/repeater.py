import regex as re


def _extended_word_tokenize(text, tokenizer):
  items = []
  for m in re.finditer(r"([^\u1780-\u17ff\s]+)|([\u1780-\u17ff\s]+)", text):
    if m.group(1):
      items.append(m.group(1))
      continue

    for item in tokenizer(m.group(2)):
      whitelisted_items = ["ឯទៀត"]
      skipped = False
      for whitelist in whitelisted_items:
        if item.endswith(whitelist) and item != whitelist:
          items.append(item[: -len(whitelist)])
          items.append(whitelist)
          skipped = True

      if skipped:
        continue

      items.append(item)
      continue

  return items


# how much text before a ៗ is tokenized to find the word(s) it repeats
WINDOW = 120
RE_REPEAT_MARK = re.compile(r"[^\S\r\n]*ៗ+")


# both spellings are common: ម្ដង (coeng da) and ម្តង (coeng ta)
ONCE = {"ម្ដង", "ម្តង"}


def _repeated(tokens):
  """the word(s) a ៗ right after `tokens` stands for"""
  # a space ends the phrase: "រៀងរាល់ថ្ងៃ ម្ដងៗ" repeats ម្ដង only
  while tokens and not tokens[-1].strip():
    tokens = tokens[:-1]
  for i in range(len(tokens) - 1, -1, -1):
    if not tokens[i].strip():
      tokens = tokens[i + 1 :]
      break
  tokens = tokens[-3:]
  if not tokens:
    return None
  if len(tokens) == 1:
    return tokens[0]

  replacement = None
  if tokens[-2] in set(["1", "មួយ", "ទាំង", "លើក"]):
    replacement = "".join(tokens[-2:])

  if tokens[-1] in {"ឡើង", "ទៅ", "ទៀត"} | ONCE:
    if tokens[-2] in {"ម៉ោង", "ថ្ងៃ", "ខែ", "ឆ្នាំ", "សប្ដាហ៍", "សប្តាហ៍", "អាទិត្យ", "យប់"}:
      replacement = "".join(tokens[-3:])
    elif tokens[-2] in set(["ពេល"]):
      replacement = tokens[-1]
    else:
      replacement = "".join(tokens[-2:])

  if tokens[-2] == "ម្នាក់" and tokens[-1] in ONCE:
    replacement = "".join(tokens[-2:])

  if tokens[-1] == "ម្នាក់" and tokens[-2] in ONCE:
    replacement = "".join(tokens[-2:])

  # fallback to one word
  return tokens[-1] if replacement is None else replacement


def processor(text, tokenizer, sep="▁"):
  """Expands the repetition mark ៗ: "ក្មេងៗ" -> "ក្មេង▁ក្មេង".

  `tokenizer` segments Khmer text into words, e.g. `khmercut.nn.tokenize`.
  A space before the mark is dropped ("ក្មេង ៗ" is "ក្មេងៗ"), a mark with
  nothing before it is removed.
  """
  if "ៗ" not in text:
    return text

  def replace(m):
    before = text[max(0, m.start() - WINDOW) : m.start()]
    before = before[before.rfind("\n") + 1 :]  # never repeat from the line above
    replacement = _repeated(_extended_word_tokenize(before, tokenizer))
    return "" if replacement is None else sep + replacement

  return RE_REPEAT_MARK.sub(replace, text)

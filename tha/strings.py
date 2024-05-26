def overwrite_spans(text, replacements):
  replacements.sort(reverse=True)
  for start, end, replacement in replacements:
    start = max(start, 0)
    end = min(end, len(text))
    text = text[:start] + replacement + text[end:]
  return text

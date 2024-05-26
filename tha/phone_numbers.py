import regex as re
from phonenumbers import PhoneNumberMatcher
from tha.strings import overwrite_spans

RE_NON_NUMBER = re.compile(r"[^\d+]+")


def processor(text: str, chunk_size=2, delimiter="▁", country_code="KH") -> str:
  replacements = []
  for m in PhoneNumberMatcher(text, country_code):
    phone_number = str(m.number.national_number)
    carrier_code = phone_number[:2]
    phone_number_id = phone_number[2:]
    i = 0
    chunks = []
    while i < len(phone_number_id):
      c = phone_number_id[i : i + chunk_size]
      if len(c) == chunk_size:
        chunks.append(c)
      else:
        chunks[-1] += c
      i += chunk_size
    digits = []
    for chunk in chunks:
      for i, c in enumerate(chunk):
        digits.append(c)
        if c != "0":
          digits[-1] = chunk[i:]
          break
    normalized = delimiter.join(digits)
    result = f"0{delimiter}{carrier_code}{delimiter}{normalized}"
    replacements.append((m.start, m.end, result))
  return overwrite_spans(text, replacements)

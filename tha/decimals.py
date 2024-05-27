import regex as re
from tha.cardinals import processor as cardinals_processor

RE_DECIMALS = re.compile(r"([\-]?[\u17e0-\u17e90-9]+)([\.\,])([\u17e0-\u17e90-9]+)")
RE_NUM_LEADING_ZEROS = re.compile(
  r"([\-]?[\u17e0-\u17e90-9]+)([\.\,])([\u17e00]+)([\d\u17e0-\u17e9]+)"
)

def processor(text: str, comma_word="ក្បៀស", point_word="ចុច") -> str:
  translation = str.maketrans({".": f"▁{point_word}▁", ",": f"▁{comma_word}▁"})

  def leading_zeros_replacer(m):
    return f"{m[1]}{m[2]}{'▁'.join(m[3])}▁{m[4]}".translate(translation)

  def decimals_replacer(m):
    sep = m[2].translate(translation)
    return f"{m[1]}{sep}{m[3]}"

  text = RE_NUM_LEADING_ZEROS.sub(leading_zeros_replacer, text)
  text = RE_DECIMALS.sub(decimals_replacer, text)
  text = cardinals_processor(text)

  return text

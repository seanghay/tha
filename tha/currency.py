import regex as re
from tha.strings import overwrite_spans
from tha.cardinals import cardinal_processor, processor as cardi_processor
from tha.decimals import processor as decimals_processor
from tha.verbatim import verbatim_dict

verbtim_translator = str.maketrans(verbatim_dict)

RE_NUM_CURRENCY = re.compile(
  r"([\$€£៛₫₽¥₩฿₭])\s?([\d\u17e0-\u17e9]+\.?[\d\u17e0-\u17e9]*)"
)

RE_MONEY_LEADING_ZEROS = re.compile(r"^[0\u17e0]+")
RE_MONEY_USD_DECIMAL = re.compile(
  r"\$ ?(([\d\u17e0-\u17e9]+,)*[\d\u17e0-\u17e9]+)(\.[\d\u17e0-\u17e9]+)?|(([\d\u17e0-\u17e9]+,)*[\d\u17e0-\u17e9]+)(\.[\d\u17e0-\u17e9]+)? ?\$"
)


def reoder(text: str) -> str:
  return RE_NUM_CURRENCY.sub(r"\2▁\1", text)


def currency_usd(
  text: str, currency_text="ដុល្លារ", cent_text="សេន", separator="▁"
) -> str:
  replacements = []
  max_precision = 2
  for m in RE_MONEY_USD_DECIMAL.finditer(text):
    cadinal = m[4] or m[1]
    floating_point = m[6] or m[3]
    if floating_point is None or len(floating_point) > max_precision + 1:
      continue

    cadinal = cadinal.replace(",", "")
    cadinal = RE_MONEY_LEADING_ZEROS.sub("", cadinal)
    floating_point = floating_point[1:]

    if len(floating_point) == 1:
      floating_point += "0" * (max_precision - len(floating_point))  # pad zeros

    floating_point = RE_MONEY_LEADING_ZEROS.sub("", floating_point)
    text_segments = []

    if cadinal:
      text_segments.append(cardinal_processor(int(cadinal)) + currency_text)

    if floating_point:
      text_segments.append(cardinal_processor(int(floating_point)) + cent_text)

    # zero
    if not floating_point and not cadinal:
      text_segments.append(cardinal_processor(int(0)) + currency_text)

    replacements.append((m.start(), m.end(), separator.join(text_segments)))
  return overwrite_spans(text, replacements)


def processor(text: str):
  text = currency_usd(text)
  text = reoder(text)
  text = decimals_processor(text)
  text = cardi_processor(text)
  return text.translate(verbtim_translator)

## Tha (ថា)

Khmer Text Normalization and Verbalization Toolkit.


## Install

```shell
pip install tha
```

`tha` builds its grammars with [pynini](https://github.com/kylebgorman/pynini). PyPI only has pynini wheels for Linux, on macOS install it from conda-forge first (or build it, see [Development](#development)):

```shell
conda install -c conda-forge pynini
```

## Verbalization

Numbers, money, measures, dates, times, phone numbers, URLs, e-mails and license plates are verbalized with weighted finite-state transducers, in the same way as [NeMo text processing](https://github.com/NVIDIA/NeMo-text-processing): the text is tagged into semiotic tokens, then each token is verbalized. Parts of a single token are joined with `▁`.

```python
import tha

tha.normalize_text("ទិញនៅ 02/01/2024 តម្លៃ $1.05")
# ទិញនៅ ថ្ងៃទី▁ពីរ▁ខែ▁មករា▁ឆ្នាំ▁ពីរពាន់▁ម្ភៃបួន តម្លៃ មួយ▁ដុល្លារ▁ប្រាំ▁សេន

normalizer = tha.Normalizer()  # compiling the grammars takes ~2s, reuse it
normalizer.tag("$1.05")
# tokens { money { integer_part: "មួយ" currency_maj: "ដុល្លារ" fractional_part: "ប្រាំ" currency_min: "សេន" } }
```

| Class | Input | Output |
| --- | --- | --- |
| cardinal | `1,234` `១.០០០` `-5` `ថ្ងៃទី០៩` `#5` | `មួយពាន់▁ពីររយ▁សាមសិបបួន` `មួយពាន់` `ដក▁ប្រាំ` `ថ្ងៃទីប្រាំបួន` `លេខ▁ប្រាំ` |
| decimal | `12.5` `0.001` `1,5` | `ដប់ពីរ▁ចុច▁ប្រាំ` `សូន្យ▁ចុច▁សូន្យ▁សូន្យ▁មួយ` `មួយ▁ក្បៀស▁ប្រាំ` |
| ordinal | `21st` | `ទី▁ម្ភៃមួយ` |
| money | `$1.05` `100 KHR` `$5 លាន` | `មួយ▁ដុល្លារ▁ប្រាំ▁សេន` `មួយរយ▁រៀល` `ប្រាំ▁លាន▁ដុល្លារ` |
| measure | `5km` `12.5%` `-3°C` | `ប្រាំ▁គីឡូម៉ែត្រ` `ដប់ពីរ▁ចុច▁ប្រាំ▁ភាគរយ` `ដក▁បី▁អង្សាសេ` |
| time | `10:23` `9:05pm` `8h30` | `ម៉ោង▁ដប់▁ម្ភៃបី▁នាទី` `ម៉ោង▁ប្រាំបួន▁ប្រាំ▁នាទី▁យប់` `ម៉ោង▁ប្រាំបី▁សាមសិប▁នាទី` |
| date | `2024-01-02` `02/01/2024` | `ថ្ងៃទី▁ពីរ▁ខែ▁មករា▁ឆ្នាំ▁ពីរពាន់▁ម្ភៃបួន` |
| telephone | `012 345 678` `+855 12 345 678` | `សូន្យ▁ដប់ពីរ▁សាមសិបបួន▁ហាសិបប្រាំមួយ▁ចិតសិបប្រាំបី` |
| electronic | `john.doe@gmail.com` | `john▁dot▁doe▁at▁g▁mail▁dot▁com` |
| license plate | `2AB-4444` | `ពីរ▁អេ▁ប៊ី▁ការ៉េ▁បួន` |
| code | `U19` `5G` `MH370` | `យូ▁ដប់ប្រាំបួន` `ប្រាំ▁ជី` `អឹម▁អេច▁បីរយ▁ចិតសិប` |
| formation | `4-4-2` | `បួន▁បួន▁ពីរ` |
| year range | `2022/23` | `ពីរពាន់▁ម្ភៃពីរ▁ដល់▁ពីរពាន់▁ម្ភៃបី` |
| serial | `192.168.0.1` `1,2,3` | `មួយរយ▁កៅសិបពីរ▁ចុច▁...` `មួយ,ពីរ,បី` |
| fraction | `3/4` `1½` | `បី▁ភាគ▁បួន` `មួយ▁និង▁មួយ▁ភាគ▁ពីរ` |
| roman | `ជំពូក II` | `ជំពូក▁ពីរ` |
| range / score | `2-3` `8:00-17:00` `ឈ្នះ ១-០` | `ពីរ▁ដល់▁បី` `ម៉ោង▁ប្រាំបី▁ដល់▁ម៉ោង▁ដប់ប្រាំពីរ` `ឈ្នះ មួយ▁ទល់▁សូន្យ` |
| size | `5x20` | `ប្រាំ▁គុណ▁ម្ភៃ` |
| whitelist | `ព.ស.` `COVID-19` | `ពុទ្ធសករាជ` `កូវីដ▁ដប់ប្រាំបួន` |

Word lists (units, currencies, months, TLDs, symbols, abbreviations, latin letter names, ...) live in [`tha/fst/data`](tha/fst/data).

Two readings depend on the text and can be turned off:

```python
# 1.000 is one thousand (the usual meaning in Khmer text), N-N is a score (ទល់)
# in lines about sports and a range (ដល់) otherwise
tha.Normalizer(dot_thousands=True, scores=True)
```

### TTS / ASR datasets

The output is meant to be the spoken form: the repetition mark `ៗ` is expanded with the [khmercut](https://github.com/seanghay/khmercut) word segmenter (`ក្មេងៗ` → `ក្មេង▁ក្មេង`, pass `word_tokenizer=False` to keep it), `៘` is left as it is, every digit is verbalized, pronounceable symbols (`&`, `+`, `=`, `@`, `%`, `$`, `°`, ...) are spoken even outside of numbers, and words already in the text aren't repeated (`ថ្ងៃទី 02/01/2024`, `ម៉ោង 8:30`). Punctuation (`។`, `,`, `-`, `/`, ...) and latin words are kept as they are, strip them afterwards if your transcripts shouldn't contain them.

The `▁` joining the parts of a token can be changed, e.g. to a space or nothing:

```python
tha.Normalizer(separator=" ").normalize("$1.05")  # មួយ ដុល្លារ ប្រាំ សេន
tha.Normalizer(separator="").normalize("$1.05")   # មួយដុល្លារប្រាំសេន
```

A typical pipeline cleans the text first:

```python
import tha
import tha.normalize

normalizer = tha.Normalizer()
normalizer.normalize(tha.normalize.processor(text))
```

## Inverse text normalization

The other way around, spoken Khmer back to its written form, e.g. for ASR transcripts. It is built the same way: the text is tagged, then every token is written.

```python
import tha

tha.inverse_normalize_text("ទិញនៅ ថ្ងៃទី▁ពីរ▁ខែ▁មករា▁ឆ្នាំ▁ពីរពាន់▁ម្ភៃបួន តម្លៃ មួយ▁ដុល្លារ▁ប្រាំ▁សេន")
# ទិញនៅ 02/01/2024 តម្លៃ $1.05

inverse = tha.InverseNormalizer()  # reuse it, like Normalizer
inverse.inverse_normalize("ប្រជាជនប្រហែលដប់ប្រាំពីរលាននាក់")
# ប្រជាជនប្រហែល17,000,000នាក់
inverse.tag("មួយ▁ដុល្លារ▁ប្រាំ▁សេន")
# tokens { money { currency: "$" integer_part: "1" fractional_part: "05" } }
```

| Class | Input | Output |
| --- | --- | --- |
| cardinal | `មួយពាន់ពីររយសាមសិបបួន` `ដប់ពាន់` `សាមប្រាំ` `ទីបី` | `1234` `10,000` `35` `ទី3` |
| decimal | `ដប់ពីរចុចប្រាំ` `មួយក្បៀសប្រាំ` | `12.5` `1,5` |
| money | `មួយដុល្លារប្រាំសេន` `មួយរយរៀល` `មួយចុចប្រាំលានដុល្លារ` | `$1.05` `100៛` `$1.5 លាន` |
| measure | `ប្រាំគីឡូម៉ែត្រ` `ដប់ពីរចុចប្រាំភាគរយ` | `5 km` `12.5%` |
| time | `ម៉ោងដប់ម្ភៃបីនាទី` `ម៉ោងប្រាំបីកន្លះ` | `10:23` `8:30` |
| date | `ថ្ងៃទីពីរ ខែមករា ឆ្នាំពីរពាន់ម្ភៃបួន` | `02/01/2024` |
| telephone | `សូន្យដប់ពីរសាមសិបបួនហាសិបប្រាំមួយចិតសិបប្រាំបី` | `012 345 678` |
| electronic | `john dot doe at gmail dot com` | `john.doe@gmail.com` |
| license plate | `ពីរអេប៊ីការ៉េបួន` | `2AB-4444` |
| fraction | `បីភាគបួន` `មួយនិងមួយភាគពីរ` | `3/4` `1 1/2` |
| range / score | `ពីរដល់បី` `មួយទល់សូន្យ` | `2-3` `1-0` |
| serial | `មួយរយកៅសិបពីរចុច...ចុចមួយ` | `192.168...1` |

- Number words are read glued together as Khmer is written (`មួយរយម្ភៃ`), or joined with `▁` or a zero width space. A space is a phrase boundary: `ពីររយ ហាសិប` is two numbers, 200 and 50. Dates may have spaces between their parts (`ថ្ងៃទីពីរ ខែមករា ឆ្នាំ...`).
- A single digit on its own stays a word (`មួយចំនួន`, `ប្រាំនាក់`), except after `ទី` and `លេខ`. Number words inside other words are left alone (`ពីរោះ`, `រយៈ`).
- The period of a time stays a word (`ម៉ោងប្រាំបួន យប់` → `9:00 យប់`), and so does a partial date (`ថ្ងៃទីពីរ ខែមករា` → `ថ្ងៃទី2 ខែមករា`).
- `ដក` before a number is a minus sign (`ដកដប់` → `-10`, `ដកដប់អង្សាសេ` → `-10°C`), between two numbers it stays a word (`ម្ភៃដកដប់` → `20ដក10`). Roman numerals, codes (`U19`) and the whitelist aren't read back.

```python
tha.InverseNormalizer(thousands_sep="")        # 10000 instead of 10,000
tha.InverseNormalizer(khmer_digits=True)       # ១០,០០០ instead of 10,000
```

## Text cleanup

```python
import tha.normalize
import tha.hashtags
import tha.ascii_lines
import tha.parenthesis
import tha.repeater

## Normalize
assert tha.normalize.processor("មិន\u200bឲ្យ") == "មិនឱ្យ"

## Hashtags
assert tha.hashtags.processor("Hello world #លុប hello") == "Hello world  hello"

## ASCII Lines
assert tha.ascii_lines.processor("Remove --- asdasd") == "Remove  asdasd"

## Parenthesis
assert tha.parenthesis.processor("Hello (this will be ignored) world") == "Hello world"


## Iteration Mark
def fake_tokenizer(_):
  return ["គាត់", "បាន", "ទៅ", "បន្តិច", "ម្ដង"]


assert (
  tha.repeater.processor("គាត់បានទៅបន្តិចម្ដងៗហើយ", tokenizer=fake_tokenizer)
  == "គាត់បានទៅបន្តិចម្ដង▁បន្តិចម្ដងហើយ"
)
```

## Development

The project is managed with [uv](https://docs.astral.sh/uv/):

```shell
uv sync        # creates .venv with the dependencies and ruff
make test      # uv run python tests.py
make lint      # ruff check + format check
make build     # uv build -> dist/
```

On Linux pynini installs from a wheel. On macOS uv builds it from source, against [OpenFst](https://www.openfst.org) from Homebrew:

```shell
brew install openfst
CPPFLAGS="-I$(brew --prefix)/include" LDFLAGS="-L$(brew --prefix)/lib" uv sync
```

uv caches the built wheel, so the flags are only needed the first time.

## Tha (ថា)

Khmer text normalization: turn written text into spoken words for TTS, and spoken words back into written text for ASR.

## Install

```shell
pip install tha
```

Tha needs [pynini](https://github.com/kylebgorman/pynini). On macOS, install it from conda-forge first:

```shell
conda install -c conda-forge pynini
```

## Written to spoken

```python
import tha

tha.normalize_text("ទិញនៅ 02/01/2024 តម្លៃ $1.05")
# ទិញនៅ ថ្ងៃទី▁ពីរ▁ខែ▁មករា▁ឆ្នាំ▁ពីរពាន់▁ម្ភៃបួន តម្លៃ មួយ▁ដុល្លារ▁ប្រាំ▁សេន
```

| Input | Output |
| --- | --- |
| `1,234` | `មួយពាន់▁ពីររយ▁សាមសិបបួន` |
| `12.5%` | `ដប់ពីរ▁ចុច▁ប្រាំ▁ភាគរយ` |
| `5km` | `ប្រាំ▁គីឡូម៉ែត្រ` |
| `10:23` | `ម៉ោង▁ដប់▁ម្ភៃបី▁នាទី` |
| `012 345 678` | `សូន្យ▁ដប់ពីរ▁សាមសិបបួន▁ហាសិបប្រាំមួយ▁ចិតសិបប្រាំបី` |
| `-5` | `ដក▁ប្រាំ` |

It also handles ordinals, fractions, phone numbers, e-mails, license plates, ranges, scores and more. Words of one number are joined with `▁`, which you can change:

```python
normalizer = tha.Normalizer(separator=" ")  # reuse it, loading takes ~2s
normalizer.normalize("$1.05")  # មួយ ដុល្លារ ប្រាំ សេន
```

## Spoken to written

```python
import tha

tha.inverse_normalize_text("ទិញនៅថ្ងៃទីពីរខែមករាឆ្នាំពីរពាន់ម្ភៃបួនតម្លៃមួយដុល្លារប្រាំសេន")
# ទិញនៅ02/01/2024តម្លៃ$1.05
```

| Input | Output |
| --- | --- |
| `ដប់ពាន់` | `10,000` |
| `ម៉ោងប្រាំបីកន្លះ` | `8:30` |
| `ដកដប់អង្សាសេ` | `-10°C` |
| `ម្ភៃដកដប់` | `20 - 10` |
| `មួយចំនួន` | `មួយចំនួន` |
| `ពីរោះ` | `ពីរោះ` |

A single number word on its own stays a word, and number words inside other words are left alone. For Khmer digits, use `tha.InverseNormalizer(khmer_digits=True)`.

## Text cleanup

```python
import tha.normalize
import tha.hashtags
import tha.parenthesis

tha.normalize.processor("មិន​ឲ្យ")                  # មិនឱ្យ
tha.hashtags.processor("Hello world #លុប hello")           # Hello world  hello
tha.parenthesis.processor("Hello (ignored) world")        # Hello world
```

## Development

```shell
uv sync
make test
```

On macOS, pynini is built from source, so install OpenFst first:

```shell
brew install openfst
CPPFLAGS="-I$(brew --prefix)/include" LDFLAGS="-L$(brew --prefix)/lib" uv sync
```

## Citation

```bibtex
@misc{yath2026tha,
  author = {Yath, Seanghay},
  title  = {Tha: Weighted Finite-State Text Normalization and Inverse Text Normalization for Khmer},
  year   = {2026},
  url    = {https://github.com/seanghay/tha}
}
```

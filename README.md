## Tha (ថា)

Khmer Text Normalization and Verbalization Toolkit.


## Install

```shell
pip install tha
```

```python
import tha.normalize
import tha.phone_numbers
import tha.urls
import tha.datetime
import tha.hashtags
import tha.ascii_lines
import tha.license_plate
import tha.cardinals
import tha.decimals
import tha.ordinals
import tha.currency
import tha.parenthesis
import tha.repeater

## Normalize
assert tha.normalize.processor("មិន\u200bឲ្យ") == "មិនឱ្យ"

## Phone Numbers
assert tha.phone_numbers.processor("010123123", chunk_size=2) == "0▁10▁12▁31▁23"
assert tha.phone_numbers.processor("010123123", chunk_size=3) == "0▁10▁123▁123"
assert tha.phone_numbers.processor("0961231234", chunk_size=3) == "0▁96▁123▁1234"

## URLs and emails
assert tha.urls.processor("example@gmail.com") == "example at g▁mail dot com"
assert tha.urls.processor("https://google.com") == "google dot com"
assert tha.urls.processor("http://google.com") == "google dot com"
assert tha.urls.processor("google.com") == "google dot com"
assert tha.urls.processor("google.gov.kh") == "google dot gov dot k▁h"
assert tha.urls.processor("google.com.kh") == "google dot com dot k▁h"

## Time
assert tha.datetime.time_processor("10:23AM") == "10 23▁A▁M"
assert tha.datetime.time_processor("10:23PM") == "10 23▁P▁M"
assert tha.datetime.time_processor("1:23PM") == "1 23▁P▁M"

## Date
assert tha.datetime.date_processor("2024-01-02") == "2024 01 02"
assert tha.datetime.date_processor("01-02-2034") == "01 02 2034"

## Hashtags
assert (
  tha.hashtags.processor("Hello world #this_will_remove hello") == "Hello world  hello"
)
assert tha.hashtags.processor("Hello world #លុប hello") == "Hello world  hello"
assert tha.hashtags.processor("Hello world #លុប1234 hello") == "Hello world  hello"

## ASCII Lines
assert tha.ascii_lines.processor("Remove --- asdasd") == "Remove  asdasd"
assert tha.ascii_lines.processor("Remove\n###\nasdasd") == "Remove\n\nasdasd"

## Cambodia License Plate
assert tha.license_plate.processor("1A 1234") == "1 A 12▁34"
assert tha.license_plate.processor("1A 4444") == "1 A ការ៉េ4"

## Number - Cardinals
assert tha.cardinals.processor("1234") == "មួយពាន់▁ពីររយ▁សាមសិបបួន"
assert tha.cardinals.processor("1") == "មួយ"
assert tha.cardinals.processor("1▁2") == "មួយ▁ពីរ"
assert tha.cardinals.processor("-1") == "ដក▁មួយ"
assert tha.cardinals.processor("10") == "ដប់"
assert tha.cardinals.processor("15") == "ដប់ប្រាំ"
assert tha.cardinals.processor("100") == "មួយរយ"
assert tha.cardinals.processor("10000") == "មួយម៉ឺន"
assert tha.cardinals.processor("10000.234") == "មួយម៉ឺន.ពីររយ▁សាមសិបបួន"
assert tha.cardinals.processor("-10000.234") == "ដក▁មួយម៉ឺន.ពីររយ▁សាមសិបបួន"
assert tha.cardinals.processor("-10000,234") == "ដក▁មួយម៉ឺន,ពីររយ▁សាមសិបបួន"

## Number - Decimals
assert tha.decimals.processor("123.324") == "មួយរយ▁ម្ភៃបី▁ចុច▁បីរយ▁ម្ភៃបួន"
assert tha.decimals.processor("123.001") == "មួយរយ▁ម្ភៃបី▁ចុច▁សូន្យ▁សូន្យ▁មួយ"
assert tha.decimals.processor("-123.0012") == "ដក▁មួយរយ▁ម្ភៃបី▁ចុច▁សូន្យ▁សូន្យ▁ដប់ពីរ"
assert tha.decimals.processor("-123,0012") == "ដក▁មួយរយ▁ម្ភៃបី▁ក្បៀស▁សូន្យ▁សូន្យ▁ដប់ពីរ"

## Number - Ordinals
assert tha.ordinals.processor("5th") == "ទី▁ប្រាំ"
assert tha.ordinals.processor("3rd") == "ទី▁បី"
assert tha.ordinals.processor("1st") == "ទី▁មួយ"
assert tha.ordinals.processor("10th") == "ទី▁ដប់"
assert tha.ordinals.processor("10") == "10"

## Number - Currency
assert tha.currency.processor("$100.01") == "មួយរយដុល្លារ▁មួយសេន"
assert tha.currency.processor("$100") == "មួយរយ▁ដុល្លារ"
assert tha.currency.processor("100$") == "មួយរយដុល្លារ"
assert tha.currency.processor("100៛") == "មួយរយរៀល"
assert tha.currency.processor("100.32៛") == "មួយរយ▁ចុច▁សាមសិបពីររៀល"
assert tha.currency.processor("100.0032៛") == "មួយរយ▁ចុច▁សូន្យ▁សូន្យ▁សាមសិបពីររៀល"

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
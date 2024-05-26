import regex as re
from urlextract import URLExtract

domain_lookup = {
  "kh": "K▁H",
  "gmail": "g▁mail",
  "edu": "E▁D▁U",
  "org": "O▁R▁G",
  "gov": "gov",
  "per": "P▁E▁R",
  "io": "I▁O",
  "us": "U▁S",
  "sg": "S▁G",
  "ru": "R▁U",
  "th": "T▁H",
}

url_extractor = URLExtract(extract_email=True, extract_localhost=True)


def url_verbalize(url: str) -> str:
  url = re.sub(r"https?:\/\/", "", url, re.IGNORECASE)
  paths = url.split(".")
  return " dot ".join(
    map(
      lambda x: domain_lookup[x.lower()].lower() if x.lower() in domain_lookup else x,
      paths,
    )
  )


def email_verbalize(email: str) -> str:
  username, domain = email.split("@")
  return f"{username} at {url_verbalize(domain)}"


def processor(text: str) -> str:
  if url_extractor.has_urls(text):
    for url in url_extractor.gen_urls(text):
      if "@" in url:
        text = text.replace(url, email_verbalize(url))
        continue
      text = text.replace(url, url_verbalize(url))
  return text

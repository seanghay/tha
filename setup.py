import setuptools

with open("README.md", "r") as f:
  long_description = f.read()

setuptools.setup(
  name="tha",
  version="0.1.0",
  description="A Khmer Text Normalization and Verbalization Toolkit.",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/seanghay/tha",
  author="Seanghay Yath",
  author_email="seanghay.dev@gmail.com",
  license="Apache License 2.0",
  classifiers=[
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
    "Intended Audience :: Developers",
    "Natural Language :: English",
  ],
  python_requires=">3.5",
  package_dir={"tha": "tha"},
  install_requires=[
    "urlextract",
    "phonenumbers",
    "regex",
    "ftfy",
  ],
)

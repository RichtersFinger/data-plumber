from pathlib import Path
from setuptools import setup

# read contents of README
long_description = \
    (Path(__file__).parent / "README.md").read_text(encoding="utf8")

# read contents of requirements.txt
requirements = \
    (Path(__file__).parent / "requirements.txt") \
        .read_text(encoding="utf8") \
        .strip() \
        .split("\n")

setup(
    version="0.0.0",
    name="pypelines",
    description="lightweight but versatile python-framework for multi-stage information processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Steffen Richters-Finger",
    author_email="srichters@uni-muenster.de",
    license="MIT",
    license_files=("LICENSE",),
    url="https://pypi.org/project/pypelines/",
    project_urls={
        "Source": "https://github.com/RichtersFinger/pypelines"
    },
    python_requires=">=3.9, <4",
    install_requires=requirements,
    packages=[
        "pypelines",
    ],
)

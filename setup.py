from pathlib import Path
from setuptools import setup

# prepare contents of long_description
docs_title = "\n## Documentation\n"
docs_dir = "docs"
docs_ref = "[Documentation](../README.md#documentation)"
docs_ref_replacement = "[Back](#documentation)"
long_description = \
    (Path(__file__).parent / "README.md") \
        .read_text(encoding="utf8") \
        .split(docs_title)[0] + docs_title
# read documentation and append to long_description
docs_files = [
    {"file": "overview.md", "ref": "overview", "title": "Overview", "value": ""},
    {"file": "pipeline.md", "ref": "pipeline", "title": "Pipeline", "value": ""},
    {"file": "stage.md", "ref": "stage", "title": "Stage", "value": ""},
    {"file": "fork.md", "ref": "fork", "title": "Fork", "value": ""},
    {"file": "stageref.md", "ref": "stageref", "title": "StageRef", "value": ""},
    {"file": "output.md", "ref": "pipelineoutput", "title": "PipelineOutput", "value": ""},
    {"file": "array.md", "ref": "pipearray", "title": "Pipearray", "value": ""},
    {"file": "examples.md", "ref": "examples", "title": "Examples", "value": ""},
]
for doc in docs_files:
    doc["value"] = \
        (Path(__file__).parent / docs_dir / doc["file"]) \
            .read_text(encoding="utf8") \
            .replace(docs_ref, docs_ref_replacement)
# build into long_description
long_description = long_description \
    + "\n" + "\n".join(
        f"* [{d['title']}](#{d['ref']})" for d in docs_files
    ) \
    + "\n\n" + "\n".join(d["value"] for d in docs_files)

# read contents of CHANGELOG
changelog = \
    (Path(__file__).parent / "CHANGELOG.md").read_text(encoding="utf8")
long_description = \
    long_description.replace(
        "[Changelog](CHANGELOG.md)", "[Changelog](#changelog)"
    ) + "\n\n" + changelog

# read contents of requirements.txt
requirements = \
    (Path(__file__).parent / "requirements.txt") \
        .read_text(encoding="utf8") \
        .strip() \
        .split("\n")

setup(
    version="1.12.1",
    name="data-plumber",
    description="lightweight but versatile python-framework for multi-stage information processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Steffen Richters-Finger",
    author_email="srichters@uni-muenster.de",
    license="MIT",
    license_files=("LICENSE",),
    url="https://pypi.org/project/data-plumber/",
    project_urls={
        "Source": "https://github.com/RichtersFinger/data-plumber"
    },
    python_requires=">=3.10",
    install_requires=requirements,
    packages=[
        "data_plumber",
    ],
    package_data={
        "data_plumber": [
            "data_plumber/py.typed",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)

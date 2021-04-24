from pathlib import Path

from setuptools import setup

readme = Path("README.md").read_text(encoding="utf-8")
version = Path("statement_parser/version.py").read_text(encoding="utf-8")
about = {}
exec(version, about)

setup(
    name="statement-parser",
    version=about["__version__"],
    license="MIT",
    author="Jamie Hannaford",
    author_email="hi@jamie.dev",
    description="Parse and analyse SEC statements to find hidden costs.",
    long_description=readme,
    long_description_content_type="text/x-rst",
    url="https://github.com/jamiehannaford/statement-parser",
    packages=["statement_analyser"],
    zip_safe=False,
    install_requires=["requests", "bs4", "lxml"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Financial and Insurance Industry",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
    ],
    project_urls={},
)
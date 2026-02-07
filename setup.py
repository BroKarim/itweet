from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="itweet",
    version="0.1.0",
    author="BroKarim",
    author_email="brokariim@egmail.com", 
    description="CLI tool to fetch trending sources and generate tweet drafts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BroKarim/itweet",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "click>=8.1.7",
    ],
    entry_points={
        "console_scripts": [
            "itweet=itweet.cli:main",
        ]
    },
)

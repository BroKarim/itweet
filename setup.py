from setuptools import setup, find_packages

setup(
    name="itweet",
    version="0.1.0",
    description="CLI tool to fetch trending sources and generate tweet drafts",
    packages=find_packages(),
    include_package_data=True,
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

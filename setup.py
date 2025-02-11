from setuptools import setup, find_packages

setup(
    name="Crawly",
    version="0.1.0",
    author="Andrew Hernandez",
    author_email="andromedeyz@hotmail.com",
    description="A efficient web crawler in Python with customizable rules and dynamic content handling for easy data extraction.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http:/localhost:3000/pi/CrawlPy",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Natural Language :: English"
    ],
    python_requires=">=3.9",
)
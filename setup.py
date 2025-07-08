# Import required modules from setuptools for package configuration
from setuptools import setup, find_packages

# Package configuration and metadata
setup(
    # Basic package information
    name="Crawly",  # Package name as it will appear on PyPI
    version="0.1.0",  # Current version following semantic versioning
    author="Andrew Hernandez",  # Package author name
    author_email="andromedeyz@hotmail.com",  # Author's contact email
    
    # Package description
    description="A efficient web crawler in Python with customizable rules and dynamic content handling for easy data extraction.",
    
    # Long description from README file for PyPI package page
    long_description=open("README.md").read(),  # Read README.md content
    long_description_content_type="text/markdown",  # Specify README format
    
    # Package repository and source code location
    url="http://github.com/ApaxPhoenix/CrawlPy",  # GitHub repository URL
    
    # Package structure and dependencies
    packages=find_packages(),  # Automatically find all Python packages in the directory
    install_requires=open("requirements.txt").read().splitlines(),  # Read dependencies from requirements.txt
    
    # Package classification for PyPI
    classifiers=[
        "Programming Language :: Python :: 3",  # Python 3 compatibility
        "License :: OSI Approved :: MIT License",  # MIT license classification
        "Operating System :: OS Independent",  # Cross-platform compatibility
        "Topic :: Internet :: WWW/HTTP",  # Web-related functionality
        "Topic :: Software Development :: Libraries :: Python Modules",  # Library classification
        "Intended Audience :: Developers",  # Target audience
        "Natural Language :: English"  # Primary language
    ],
    
    # Python version requirement
    python_requires=">=3.9",  # Minimum Python version required
)

from setuptools import setup, find_packages

setup(
    name="nart",
    version="1.0.0",
    description="Network Assessment Reporting Tool",
    author="RedBlue Labs",
    author_email="info@redbluelabs.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "python-docx>=0.8.11",
        "matplotlib>=3.5.0",
        "numpy>=1.21.0",
        "requests>=2.28.0",
        "lxml>=4.9.0",
        "PyYAML>=6.0",
        "llama-cpp-python>=0.2.0",
        "sentence-transformers>=2.2.2",
        "PySide6>=6.5.0",
        "darkdetect>=0.8.0",
    ],
    entry_points={
        "console_scripts": [
            "nart=src.main:main",
            "nart-cli=src.cli.commands:main",
        ],
    },
    python_requires=">=3.9",
)
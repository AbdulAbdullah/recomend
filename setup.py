from setuptools import setup, find_packages

setup(
    name="bob-whisky-recommender",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Django>=4.2.7",
        "djangorestframework>=3.14.0",
        "requests>=2.31.0",
        "pandas>=2.1.1",
        "scikit-learn>=1.3.2",
        "numpy>=1.26.1",
        "python-dotenv>=1.0.0",
        "pyjwt>=2.8.0",
    ],
    author="BAXUS Team",
    author_email="team@baxus.co",
    description="AI whisky recommendation engine for BAXUS users",
    keywords="whisky, recommendation, AI, ML, BAXUS",
    python_requires=">=3.9",
)
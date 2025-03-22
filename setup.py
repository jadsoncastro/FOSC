from setuptools import setup, find_packages

setup(
    name="FOSC",
    version="0.1.1a1",
    packages=find_packages(),
    install_requires=[
        "matplotlib==3.8.2",
        "mplcursors==0.5.3",
        "networkx==3.2.1",
        "numpy==1.26.2",
        "scipy==1.11.4",
        "typing_extensions==4.12.2",
    ],
    author="Jadson Castro Gertrudes",
    author_email="jadson.castro@ufop.edu.br",
    maintainer="Matheus Neto Gurgel",
    maintainer_email="matheus.gurgel@aluno.ufop.edu.br",
    description="Framework for Optimal Extraction of Clusters",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jadsoncastro/FOSC",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

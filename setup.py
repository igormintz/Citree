#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Citree-pkg-Igor_Mintz", 
    version="0.0.1",
    author="Igor Mintz",
    author_email="igormintz@example.com",
    description="creates citation tree plot using DOI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/igormintz/Citree",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)


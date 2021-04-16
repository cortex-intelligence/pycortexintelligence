import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycortexintelligence",
    version="0.0.17",
    author="Enderson Menezes",
    scripts=["cortex.py"],
    author_email="endersonster@gmail.com",
    description="Cortex Intelligence Platform Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cortex-intelligence/pycortexintelligence",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests>=2.24.0',
        'click>=7.1.2',
    ],
)
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycortexintelligence",
    version="1.2.2-embrapa",
    author="Enderson Menezes",
    scripts=["cortex.py"],
    author_email="data.integrations@cortex-intelligence.com",
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
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "click>=7.1.2",
        "boto3>=1.21.32",
        "pandas>=1.3.5, <2.0.0",
    ],
)

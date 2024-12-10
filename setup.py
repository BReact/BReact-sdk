from setuptools import setup, find_packages

setup(
    name="breact-sdk",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    author="BReact OS Team",
    author_email="team@breactos.com",
    description="Official SDK for BReact OS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/breactos/breact-sdk",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
)
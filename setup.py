from setuptools import setup, find_packages

setup(
    name="breact-sdk",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.24.0"
    ],
    author="BReact OS Team",
    author_email="office@breact.ai",
    description="Official SDK for BReact OS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/BReact/BReact-sdk",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
)
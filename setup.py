from setuptools import setup, find_packages
import os

# Ensure README.md exists and can be read
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "BReact SDK for interacting with BReact's AI services"

setup(
    name="breactsdk",
    version="0.1.5",
    packages=find_packages(include=["breactsdk", "breactsdk.*"]),
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.24.0"
    ],
    author="BReact OS Team",
    author_email="office@breact.ai",
    description="Official SDK for BReact OS",
    long_description=long_description,
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
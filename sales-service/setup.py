from setuptools import setup, find_packages

setup(
    name="sales-service",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pydantic==2.5.2",
        "pymongo==4.6.1",
        "motor==3.3.2",
        "python-dotenv==1.0.0",
        "httpx==0.25.2"
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "pytest-cov==4.1.0"
        ]
    }
) 
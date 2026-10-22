# [1권 Chapter 14: 모듈과 패키지 · 14.11 패키지 배포하기 · manuscript/chapters/14-modules-packages.md:2459]
# setup.py (레거시 방식)
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="seoul-food-platform",
    version="1.0.0",
    author="김개발",
    author_email="dev@example.com",
    description="서울 음식점 검색 및 추천 플랫폼",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/seoul-food-platform",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "ruff>=0.1.0"],
        "web": ["fastapi>=0.100.0", "uvicorn>=0.23.0"],
    },
    entry_points={
        "console_scripts": [
            "seoul-food=seoul_food_platform.cli.main:main",
        ],
    },
)

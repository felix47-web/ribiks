from setuptools import setup, find_packages

setup(
    name="ribiks",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "telethon",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "ribiks=ribiks.cli:main",
        ],
    },
    author="Ribiks",
    description="Telegram Chat Autoreply & Group Scanner",
    python_requires=">=3.8",
)

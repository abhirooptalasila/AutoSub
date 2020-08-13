import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AutoSub", # Replace with your own username
    version="0.0.1",
    author="Abhiroop Talasila",
    author_email="abhiroop.talasila@gmail.com",
    description="Automatically generate subtitles for any video file using STT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abhirooptalasila/AutoSub",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

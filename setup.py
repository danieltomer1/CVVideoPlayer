from setuptools import setup, find_packages

setup(
    name="cvvideoplayer",
    version="1.0.0",
    author="Daniel Tomer",
    author_email="danieltomer1@gmail.com",
    description="moduler multi purpose video player for python",
    long_description=(
        "CV video player is a Python-based customizable video player that helps"
        " computer vision practitioners to develop, analyze and debug their video"
        " related algorithms and model."
    ),
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        "numpy",
        "opencv-python",
        "pynput",
        "python-xlib",
        "matplotlib",
    ],
    python_requires=">=3.8",
    project_urls={
        "Homepage": "https://github.com/danieltomer1/CVVideoPlayer",
    },
)

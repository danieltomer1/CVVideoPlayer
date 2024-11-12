from setuptools import setup, find_packages

with open("Readme.md", 'r') as f:
    long_description = f.read()

setup(
    name="cvvideoplayer",
    version="1.1.3",
    author="Daniel Tomer",
    author_email="danieltomer1@gmail.com",
    description="moduler multi purpose video player for debugging algorithms in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
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
    keywords=[
        'opencv',
        'video',
        'player',
        'video player',
        'cvvideoplayer',
        'computer vision',
        'image processing',
        'customizable'
    ]
)

from setuptools import setup, find_packages

setup(
    name="py_video_player",
    version="0.1.0",
    author="Daniel Tomer",
    author_email="danieltomer1@gmail.com",
    description="moduler multi purpose video player for python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: ubuntu",
    ],
    install_requires=[
        "numpy",
        "opencv-python",
        "pynput",
        "decord",
        "python-xlib",
        "matplotlib",
    ],
    python_requires=">=3.8",
)

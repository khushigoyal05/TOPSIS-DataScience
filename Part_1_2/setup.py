from setuptools import setup, find_packages

setup(
    name="Topsis-Khushi-102303993",
    version="1.0.0",
    author="Khushi Goyal",
    author_email="<goyalkhushi3844@gmail.com>", 
    description="A Python package for implementing TOPSIS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'topsis=Topsis_Khushi_102303993.topsis:main',
        ],
    },
)
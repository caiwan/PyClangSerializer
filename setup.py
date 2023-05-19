from setuptools import setup, find_namespace_packages

setup(
    name="gk-source-index",
    version="0.0.1",
    description="Source index and code generation with Jinja2 and Clang-index",
    long_description=open("README.md").read(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "clang==6.0.0.2",
        "more_itertools==8.12.0",
        "dataclasses_json==0.5.7",
        "PyYAML==6.0",
        "Jinja2==3.1.1",
    ],
    setup_requires=[
        "setuptools>=43.0.0",
        "wheel",
    ],
    package_dir={"": "src"},
    packages=find_namespace_packages(
        where="src",
        exclude=[
            "tests",
            "*.tests",
            "tests.*",
            "*.tests.*",
        ],
    ),
    extras_require={
        "test": [
            "pytest",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "generate-code=source_index.main:main",
            "check-clang=source_index.check_clang:main",
        ],
    },
    flake8={
        "ignore": "E203, E266, E501, W503, F403, F401",
        "max-line-length": "120",
        "max-complexity": "24",
        "select": "B,C,E,F,W,T4,B9",
    },
    black={
        "line-length": "120",
    },
    aliases={
        "test": "pytest",
    },
)

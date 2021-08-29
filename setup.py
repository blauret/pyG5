"""Setup for the  pyG5 packaging."""

from setuptools import find_packages, setup

from pyG5.pyG5Main import __version__


with open("README.md") as readme_file:
    readme = readme_file.read()


# commented out due to impossibility
# to install PyQt5 automatically from pip on Raspbian
# requirements = ["PyQt5"]
requirements = []

test_requirements = [
    # TODO: put package test requirements here
]

PackageDescription = """
    PyQt5 application connecting to X-Plane flifht simulator and displaying a garmin G5
    attitude indicator as well as Horizontal Situation indicator

"""


setup(
    name="pyG5",
    version=__version__,
    description=PackageDescription,
    long_description_content_type="text/markdown",
    long_description=readme,
    author="Ben Lauret",
    author_email="ben@lauretland.com",
    url="https://github.com/blauret/pyG5",
    packages=find_packages(where="."),
    package_dir={"pyG5": "pyG5"},
    include_package_data=True,
    install_requires=requirements,
    dependency_links=[],
    license="MIT license",
    zip_safe=False,
    keywords=["X-Plane", "python", "PyQt5", "Garmin", "G5"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
    ],
    test_suite="tests",
    scripts=[
        "Scripts/pyG5DualStacked",
    ],
    tests_require=test_requirements,
)

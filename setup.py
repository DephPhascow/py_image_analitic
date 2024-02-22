from setuptools import setup, find_packages

readme = ""
license = ""

with open("README.md", "r") as fh:
    readme = fh.read()
with open("LICENCE", "r") as fh:
    license = fh.read()
 
setup(
    name = "",
    version = "1.1.0",
    keywords = ("", ),
    description = "",
    long_description = readme,
    license = license,
    url = "",
    author = "",
    author_email = "",
    packages = find_packages(),
    include_package_data = True,
    platforms = "",
    install_requires = [""]
)
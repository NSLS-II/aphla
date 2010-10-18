from setuptools import setup, find_packages
setup(
    name = "seasail",
    version = "0.1",
    packages = find_packages(),
    install_requires = ['docutils >= 0.3'],
    description = "Accelerator control and experiment toolkit",
    author = "Guobao Shen, Lingyun Yang",
    #py_modules=['seasail.hla'],
    #package_dir={'': 'seasail'},
)


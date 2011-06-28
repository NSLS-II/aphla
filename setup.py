from setuptools import setup, find_packages
setup(
    name = "hla",
    version = "0.1.0a3",
    #packages = ['hla'],
    package_dir = {'hla': 'src/hla'},
    package_data = {'hla': ['machine/nsls2/*']},
    py_modules = ['hla.catools', 'hla.machines', 'hla.element', 'hla.lattice',
                  'hla.twiss', 'hla.hlalib', 'hla.rf', 'hla.orbit', 
                  'hla.ormdata'],
    install_requires = ['docutils >= 0.3', 'channelfinder >= 1.0'],
    description = "Accelerator control and experiment toolkit",
    author = "Lingyun Yang, Jinhyuk Choi",
    maintainer = "Lingyun Yang",
    maintainer_email = "lyyang@bnl.gov",
)


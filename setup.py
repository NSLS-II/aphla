from setuptools import setup, find_packages
setup(
    name = "hla",
    version = "0.3.0",
    #packages = ['hla'],
    data_files = {},
    package_dir = {'hla': 'src/hlalib', 'mpfit': 'src/mpfit'},
    package_data = {'hla': ['machine/nsls2/channel_finder_server.txt']},
    scripts=['src/orbit.pyw', 'src/elemtuner.py', 'src/elementpickdlg.py'],
    py_modules = ['hla.catools', 'hla.machines', 'hla.element', 'hla.lattice',
                  'hla.twiss', 'hla.hlalib', 'hla.rf', 'hla.orbit', 
                  'hla.ormdata', 'hla.orm', 'hla.aptools', 'hla.bba',
                  'hla.meastwiss'],
    install_requires = ['docutils >= 0.3', 'Sphinx >= 1.0.8', 
                        'channelfinder >= 1.0'],
    description = "Accelerator control and experiment toolkit",
    author = "Lingyun Yang, Yoshiteru Hidaka, Jinhyuk Choi",
    maintainer = "Lingyun Yang",
    maintainer_email = "lyyang@bnl.gov",
)


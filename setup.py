from setuptools import setup, find_packages
#from distutils.core import setup
#from distutils.command.sdist import sdist
import os
#from distribute_setup import use_setuptools
#use_setuptools()


setup(
    name = "aphla",
    version = "0.3.0b4",
    packages = ['aphla', 'aphla.mpfit', 'aphla.gui', 'aphla.gui.Qt4Designer_files', 
                'aphla.gui.TunerUtils', 'aphla.gui.PlotterUtils', 'aphla.conf'],
    data_files = {},
    package_dir = {'aphla': 'lib', 'aphla.mpfit': 'lib/mpfit',
                   'aphla.gui': 'gui', 'aphla.conf': 'conf'},
    #include_package_data = True,
    package_data = {'aphla.gui': ['data/*.json', 'data/*.cfg', 'data/*.hdf5'], 
                    'aphla.conf': ['us_nsls2/*', '*.csv', '*.json', '*.hdf5', '*.xml']},
    py_modules = [
                  'aphla.catools', 'aphla.chanfinder', 'aphla.machines', 'aphla.element',
                  'aphla.lattice', 'aphla.twiss', 'aphla.hlalib', 
                  'aphla.rf',
                  'aphla.ormdata', 'aphla.orm', 'aphla.aptools', 
                  'aphla.bba',
                  'aphla.meastwiss', 
                  # GUI
                  'aphla.gui.gui_resources',
                  'aphla.gui.aplauncher',
                  'aphla.gui.orbit', 'aphla.gui.orbitconfdlg', 
                  'aphla.gui.apbba'],
    install_requires = ['distribute', 'matplotlib', 'numpy >= 1.4.1', 'scipy >= 0.7'],
    entry_points = {
        'gui_scripts': [
            'aporbit = aphla.gui.orbit:main',
            'apbba = aphla.gui.apbba:main',
            'aplauncher = aphla.gui.aplauncher:main',
            'apcurrentmonitor = aphla.gui.apcurrentmonitor:main'
            ]
        },
    description = "Accelerator control and experiment toolkit",
    author = "Lingyun Yang, Yoshiteru Hidaka, Jinhyuk Choi",
    maintainer = "Lingyun Yang",
    maintainer_email = "lyyang@bnl.gov",
    )


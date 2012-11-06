from setuptools import setup, find_packages
import os


setup(
    name = "aphla",
    version = "0.5.0",
    packages = ['aphla', 'aphla.mpfit', 'aphla.gui', 'aphla.gui.Qt4Designer_files', 
                'aphla.gui.TunerUtils', 'aphla.gui.PlotterUtils', 'aphla.conf'],
    package_dir = {'aphla': 'lib', 'aphla.mpfit': 'lib/mpfit',
                   'aphla.gui': 'gui', 'aphla.conf': 'conf'},
    include_package_data = True,
    package_data = {
        # any these files
        '': ['*.json', '*.hdf5', '*.csv'],
        'aphla.gui': ['data/*.cfg'], 
        'aphla.conf': ['us_nsls2/*', '*.xml', '*.db']},
    py_modules = [
        'aphla.catools', 'aphla.chanfinder', 'aphla.machines', 'aphla.element',
        'aphla.lattice', 'aphla.twiss', 'aphla.hlalib', 
        'aphla.ormdata', 'aphla.orm', 'aphla.aptools', 
        'aphla.bba',
        'aphla.meastwiss', 
        # GUI
        'aphla.gui.gui_resources',
        'aphla.gui.aplauncher',
        'aphla.gui.channelexplorer',
        'aphla.gui.orbit', 'aphla.gui.orbitconfdlg', 
        'aphla.gui.apbba'],
    #install_requires = ['distribute', 'matplotlib', 'cothread',
    #                    'numpy', 'scipy'],
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
    url = 'http://code.nsls2.bnl.gov/hg/ap/hla',
    )


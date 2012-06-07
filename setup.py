from setuptools import setup, find_packages
#from distutils.core import setup
#from distutils.command.sdist import sdist
import os
#from distribute_setup import use_setuptools
#use_setuptools()

# class sdist_hg(sdist):

#     user_options = sdist.user_options + [
#             ('dev', None, "Add a dev marker")
#             ]

#     def initialize_options(self):
#         sdist.initialize_options(self)
#         self.dev = 0

#     def run(self):
#         if self.dev:
#             suffix = '.dev%d' % self.get_tip_revision()
#             self.distribution.metadata.version += suffix
#         sdist.run(self)

#     def get_tip_revision(self, path=os.getcwd()):
#         from mercurial.hg import repository
#         from mercurial.ui import ui
#         from mercurial import node
#         repo = repository(ui(), path)
#         tip = repo.changelog.tip()
#         return repo.changelog.rev(tip)

setup(
    name = "aphla",
    version = "0.3.0b2",
    packages = ['aphla', 'aphla.mpfit', 'aphla.gui', 'aphla.gui.Qt4Designer_files', 
                'aphla.gui.TunerUtils', 'aphla.gui.PlotterUtils', 'aphla.conf'],
    data_files = {},
    package_dir = {'aphla': 'lib', 'aphla.mpfit': 'lib/mpfit',
                   'aphla.gui': 'gui', 'aphla.conf': 'conf'},
    #include_package_data = True,
    package_data = {'aphla.gui': ['data/*.json', 'data/*.cfg', 'data/*.hdf5'], 
                    'aphla.conf': ['*.csv', '*.json', '*.hdf5', '*.xml']},
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
    install_requires = ['distribute', 'docutils>=0.3', 'Sphinx >= 1.0.8', 
                        'matplotlib', 'numpy >= 1.4.1', 'scipy >= 0.7'],
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


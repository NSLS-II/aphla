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
    name = "aphlas",
    version = "0.3.0",
    packages = ['aphlas', 'aphlas.mpfit', 'aphlas.gui'],
    data_files = {},
    package_dir = {'aphlas': 'lib', 'aphlas.mpfit': 'lib/mpfit',
                   'aphlas.gui': 'script'},
    #include_package_data = True,
    package_data = {'aphlas.gui': ['data/*.json']},
    py_modules = ['aphlas.catools', 'aphlas.machines', 'aphlas.element',
                  'aphlas.lattice', 'aphlas.twiss', 'aphlas.hlalib', 
                  'aphlas.rf', 'aphlas.orbit', 
                  'aphlas.ormdata', 'aphlas.orm', 'aphlas.aptools', 'aphlas.bba',
                  'aphlas.meastwiss', 'aphlas.gui.orbit', 'aphlas.gui.orbit_resources'],
    install_requires = ['distribute', 'docutils>=0.3', 'Sphinx >= 1.0.8', 
                        'matplotlib', 'numpy', 'scipy'],
    entry_points = {
        'gui_scripts': [
            'aporbit = aphlas.gui.orbit:main'
            ]
        },
    description = "Accelerator control and experiment toolkit",
    author = "Lingyun Yang, Yoshiteru Hidaka, Jinhyuk Choi",
    maintainer = "Lingyun Yang",
    maintainer_email = "lyyang@bnl.gov",
    )


#
#

"""
Module for HLA configuration settings
"""

import os
import re
import sys
import logging
import ConfigParser
from warnings import warn

log = logging.getLogger(__name__)

CONFIG_SYNTAX_ERROR = "There is a syntax error in your configuration file: %s"

class Config(object):
    """HLA configuration

    Instance of config are used throughout HLA to configure behavior,
    including GUI applications.
    """

    # the default values
    config_values = dict(
        channFinderServiceUrl = "http://channelfinder/ChannelFinder",
        configDir = "~/.hla",
        dataDir = "~/.hla/data",
        configFiles = [ "hlarc" ],
        )
    

    def __init__(self, **kw):
        self.env = env = kw.pop('env', os.environ)
        self.values = Config.config_values.copy()
        self._raw_configs = {}
        dirname = kw.pop("dirname", Config.config_values['configDir'])
        if os.path.exists(dirname):
            files = kw.pop("files", Config.config_values['configFiles'])
            for conf in files:
                config = {}
                cf = os.path.join(dirname, conf)
                olddir = os.getcwd()
                try:
                    os.chdir(dirname)
                    f = open(cf, 'rU')
                    try:
                        source = f.read()
                    finally:
                        f.close()
                    try:
                        code = compile(source, cf, 'exec')
                    except SyntaxError, err:
                        raise RuntimeError(CONFIG_SYNTAX_ERROR % err)
                finally:
                    os.chdir(olddir)

                self._raw_configs[cf] = config

    def initValues(self):
        for k,config in self._raw_configs.iteritems():
            if k in self.values: self.__dict__[k] = config[k]
        del self._raw_configs
                
    def configure(self):
        """
        Configure the HLA running environment
        """
        pass

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        if name not in self.values:
            raise AttributeError('No such config value: %s' % name)
        default = self.values[name]
        if hasattr(default, '__call__'):
            return default(self)
        return default

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)
        
    def __delitem__(self, name):
        delattr(self, name)


#def writeDefault(dirname = None):
#    from pkg_resources import resource_string
#    if dirname is None:
#        rt = Config.config_values['configDir']
#    else:
#        rt = dirname
#    #if not os.path.exists(rt):
#    #    os.path.makedirs(rt)
#    for f in Config.config_values['configFiles']:
#        print resource_string(__name__, '../hlalib')

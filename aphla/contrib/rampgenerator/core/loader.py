from ..loaders.ramploader import RampLoader

from ..loaders.plainramploader import PlainRampLoader
from ..loaders.steppingramploader import SteppingRampLoader
from ..loaders.fullramploader import FullRampLoader


def Loader(ltype='simple', *args, **kwargs):
    for cls in RampLoader.__subclasses__():
        if cls.is_loader_for(ltype):
            return cls(*args, **kwargs)
    return None

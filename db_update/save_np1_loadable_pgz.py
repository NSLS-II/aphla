# This script is meant to load a dictionary that contians NumPy 2.x objects
# that cannot be unpickled by NumPy older than 1.26.x, due to the backward-
# incompatible change of numpy.core to numpy._core, and then save it back to a
# .pgz file that can be loaded by an older version of aphla-v2 (before NumPy 1.26.x).

import sys
import gzip
import pickle

class Numpy2to1Unpickler(pickle.Unpickler):
    """Remap NumPy 2.x module paths (numpy._core.*) to NumPy 1.x (numpy.core.*)."""
    def find_class(self, module, name):
        if module.startswith("numpy._core"):
            module = module.replace("numpy._core", "numpy.core", 1)
        return super().find_class(module, name)

def load_numpy2_pickle_in_numpy1(path):
    with gzip.open(path, "rb") as f:
        return Numpy2to1Unpickler(f).load()


if __name__ == "__main__":
    import numpy as np
    assert np.__version__.startswith("1."), (
        "This script must be run with Python using NumPy 1.x."
    )

    try:
        np2_pgz_filepath, np1_pgz_filepath = sys.argv[1:]

        d = load_numpy2_pickle_in_numpy1(np2_pgz_filepath)

        with gzip.GzipFile(np1_pgz_filepath, "wb") as f:
            pickle.dump(d, f)

    except:
        raise ValueError(
            "Provide the input NumPy 2.x .pgz filepath and the output NumPy 1.x .pgz filepath."
        )

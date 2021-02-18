# This script should be run with v1 aphla (w/ $ ap-conda-latest)

import aphla as ap

# Available submachine names
['LN', 'LTD1', 'LTD2', 'LTB', 'BR', 'BTD', 'BTS', 'SR']

#submachine = 'SR'
#submachine = 'BTS'
#submachine = 'BTD'
#submachine = 'BR'
#submachine = 'LTB'
#submachine = 'LTD2'
#submachine = 'LTD1'
submachine = 'LN'

ap.machines.load('nsls2', submachine)

# While running "ap.machines.load('nsls2', submachine)" interactively, within load()
# in aphla/machines/__init__.py, right after "cfa.loadSqlite(accsqlite)" was
# exectuted, the contents of the list "cfa.rows" was manually saved into the
# following pgz file:
#
import gzip
import pickle
nsls2_sqlite_rows_pgz_file = f'nsls2_{submachine.lower()}_sqlite_rows.pgz'
with gzip.GzipFile(nsls2_sqlite_rows_pgz_file, 'wb') as f:
    pickle.dump(cfa.rows, f)

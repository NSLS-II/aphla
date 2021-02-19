# This script should be run with v1 aphla (w/ $ ap-conda-latest)

import aphla as ap

# Available submachine names
['LN', 'LTD1', 'LTD2', 'LTB', 'BR', 'BTD', 'BTS', 'SR']

#submachine = 'SR' # /epics/aphla/apconf/nsls2/nsls2_sr.sqlite
#submachine = 'BTS' # /epics/aphla/apconf/nsls2/nsls2_bts.sqlite
#submachine = 'BTD' # /epics/aphla/apconf/nsls2/nsls2_BTD.sqlite
submachine = 'BR' # /epics/aphla/apconf/nsls2/nsls2_BR.sqlite
#submachine = 'LTB' # /epics/aphla/apconf/nsls2/nsls2_LTB.sqlite
#submachine = 'LTD2' # /epics/aphla/apconf/nsls2/nsls2_LTD2.sqlite
#submachine = 'LTD1' # /epics/aphla/apconf/nsls2/nsls2_LTD1.sqlite
#submachine = 'LN' # /epics/aphla/apconf/nsls2/nsls2_LN.sqlite

ap.machines.load('nsls2', submachine)

if submachine == 'BR':

    bpms = ap.getElements('BPM')
    e = bpms[0]

    [(fld, e._field[fld].pvrb) for fld in e.fields()]
    [(fld, e._field[fld].pvsp) for fld in e.fields()]

    print(e.mode)
    print(e.get('mode', handle='readback', unitsys=None))
    print(e.get('mode', handle='setpoint', unitsys=None))

import sys
sys.exit(0)

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

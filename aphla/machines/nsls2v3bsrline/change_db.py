from aphla import chanfinder
from fnmatch import fnmatch

def main():
    cfa = chanfinder.ChannelFinderAgent()
    cfa._importSqliteDb1("us_nsls2v3bsrline.sqlite")
    for v1,v2 in [('name', 'elemName'), ('elem_type', 'elemType'), 
                  ('handle', 'elemHandle'), ('polar', 'elemPolar'),
                  ('position', 'elemPosition'), ('length', 'elemLength'),
                  ('elem_field', 'elemField'), ('tracy_el_idx_va', 'elemIndex'),
    ]:
        cfa.renameProperty(v1, v2)
    for r in cfa.rows:
        for k in ['tracy_el_type_va', 'angle', 'elem_id', 'lat_index', 
                  'tracy_machine', 'k1', 'k2', 'tracy_el_field_va',
                  'tracy_el_name_va', 'elem_group', 'virtual',
                  'high_lim', 'low_lim', 'system']:
            r[1].pop(k, None)

    kept = []
    # remove y field for c1-7, brcx1se
    for r in cfa.rows:
        name = r[1]['elemName']
        #print name, r[1]['elemType']
        #if r[1]['elemType'].startswith('TRI'): print r[0]

        if fnmatch(name, 'c[1-7]') or name in ['brcx1se']:
            if r[1]['elemField'] == 'y': continue
        kept.append(r)

    cfa.rows = kept
    #cfa._export_csv_2("test.csv")
    cfa.exportSqlite("nsls2v3bsrline.sqlite")

if __name__ == "__main__":
    main()



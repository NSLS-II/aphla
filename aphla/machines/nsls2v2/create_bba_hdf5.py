#
import numpy as np
import aphla as ap
import h5py

def create(g, q, qf, c, cf, b, bf):
    newname = "%s.%s:%s.%s:%s.%s" % (q.name, qf, c.name, cf, b.name, bf)
    print newname
    qr = g.create_group(str(newname))
    qr.attrs['quad_dkick'] = -6e-2
    qr.attrs['cor'] = [str(c.name), str(cf), 
                       str(c.pv(field=cf, handle='setpoint'))]
    qr.attrs['bpm'] = [str(b.name), str(bf), 
                       str(b.pv(field=bf, handle='readback'))]
    qr.attrs['cor_kick'] = np.linspace(-6e-6, 1e-5, 5)
    qr.attrs['cor_unit'] = 'phy'


def main(fname, grp = "bba"):
    f = h5py.File(fname, 'w')
    g = f.create_group(grp)

    ap.machines.init("nsls2v2")
    ap.machines.use("V2SR")
    for q in ap.getElements("QUAD"):
        vb = ap.getClosest(q, 'BPM')
        c = ap.getNeighbors(q, 'COR', 1)[0]

        create(g, q, 'g', c, 'x', vb, 'x')
        create(g, q, 'g', c, 'y', vb, 'y')
        f.flush()
    f.close()

if __name__ == "__main__":
    main("v2sr_bba.hdf5", "bba")

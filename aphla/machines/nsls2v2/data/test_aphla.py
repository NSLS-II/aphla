import aphla as ap
ap.enableLog("aphla.log")
ap.machines.load("nsls2v2")
print "Lattices:", ap.machines.lattices()
print "Elements:", len(ap.getElements("*"))
for i,e in enumerate(ap.getElements("c*")):
    print i, e.pv(field='x', handle="readback"), \
        e.pv(field='x', handle="setpoint")

for i,e in enumerate(ap.getElements("SEXT")):
    print i, e.name, e.pv(field="b2", handle="readback"), \
        e.pv(field='b2', handle="setpoint")



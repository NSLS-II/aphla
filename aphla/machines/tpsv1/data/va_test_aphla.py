import aphla as ap
ap.enableLog("aphla.log")
ap.machines.load("tpsv1")
print "Elements:", len(ap.getElements("*"))
for i,e in enumerate(ap.getElements("c*")):
    print i, e.pv(field='x', handle="readback"), \
        e.pv(field='x', handle="setpoint")


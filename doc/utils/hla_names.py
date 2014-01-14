"""
autogenerate some tables for aphla namespace
"""
# :author: Lingyun Yang <lyyang@bnl.gov>

from aphla import *
ignored_commands = [
    'ChannelFinderAgent', 'NullHandler', 'OrmData', 'caget', 'caput',
    'addGroup', 'addGroupMembers', 'caRmCorrect', 'caputwait',
    'getCurrentMode', 'getModes', 'removeGroup', 'removeGroupMembers',
    'saveMode', 'waitChanged', 'waitStable', 'waitStableOrbit', 'fnmatch']

d = locals()
keys = d.keys()
keys.sort()

modd = dict()
for k in keys:
    o = d[k]
    if not callable(o):
        continue
    doc = getattr(o, '__doc__', None)
    if doc is not None:
        #doc = ' - '.join([line for line in doc.split('\n') if line.strip()][:2])
        doclst = [line for line in doc.split('\n') if line.strip()]
        doc = doclst[0]
    
    mod = getattr(o, '__module__', None)
    if mod is None:
        mod = 'unknown'
    else:
        if mod.startswith('aphla'):
            if k in ignored_commands: doc = None
            elif k[0].isupper():
                k = ':class:`~%s.%s`'%(mod, k)
            else:
                k = ':func:`~%s.%s`'%(mod, k)
            mod = ':mod:`%s`'%mod            
        elif mod.startswith('numpy'):
            #k = '`%s <%s>`_'%(k, 'http://scipy.org/Numpy_Example_List_With_Doc#%s'%k)
            k = '`%s <%s>`_'%(k, 'http://sd-2116.dedibox.fr/pydocweb/doc/%s.%s'%(mod, k))
        elif mod.startswith('cothread'):
            k = '`%s <%s>`_'%(k, 'http://controls.diamond.ac.uk/downloads/python/cothread/')
        else:
            continue
    if doc is None: continue
    
    mod, k, doc = mod.strip(), k.strip(), doc.strip()[:80]
    #print mod, k, doc
    if mod.startswith('cothread'): continue

    #modd.setdefault(mod, []).append((k, doc))
    modd.setdefault('aphla', []).append((k, doc))

#print "Commands"
#print "========"
#print ""
#print ".. toctree::"
#print "   :maxdepth: 2"
#print ""
#print ".. htmlonly::"
#print "   :Date: |today|"
#print ""
#print "Function List"
#print "-------------"
#print ""

mods = modd.keys()
mods.sort()
for mod in mods:
    #border = '*'*len(mod)
    # skip the mod
    #print mod
    #print border
    
    N = 10
    print
    funcs, docs = zip(*modd[mod])
    maxfunc = max([len(f) for f in funcs])
    maxdoc = max(120, max([len(d) for d in docs]) )
    border = ' '.join(['='*(maxfunc), '='*maxdoc])
    print border
    print ' '.join(['symbol'.ljust(maxfunc), 'description'.ljust(maxdoc)])
    print border
    for func, doc in modd[mod]:
        #
        #if any([func.endswith(f+'`') for f in ignored_commands]): continue
        row = ' '.join([func.ljust(maxfunc), doc.ljust(maxfunc)])
        print row

    print border
    print
    #break

#print "Complete Reference"
#print "------------------"
#print ""

#for m in ['catools', 'chanfinder', 'element', 'lattice', 'machines', 'twiss', 
#          'hlalib', 'ormdata', 'orm', 'aptools', 'bba', 'meastwiss']:
#    print ".. automodule:: aphla.%s" % m
#    print "   :members:"
#    print ""


#for mod in mods:
#    if not mod.startswith(':mod'): continue
#    print ".. automodule::", mod[6:-1]
#    print "   :members:"
#    print ""
    

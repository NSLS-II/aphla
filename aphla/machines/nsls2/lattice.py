
def _initNSLS2(cfa):
    """ 
    initialize the NSLS2 accelerator lattice 'SR', 'LTD1', 'LTD2', 'LTB'.

    The initialization is done in the following order:

        - user's `${HOME}/.hla/us_nsls2.sqlite`; if not then
        - channel finder service in `env ${HLA_CFS_URL}`; if not then
        - the `us_nsls2.sqlite` installed with aphla package; if not then
        - RuntimeError
    """

    cfa = ChannelFinderAgent()
    cfs_filename = 'us_nsls2.sqlite'
    src_home_csv = os.path.join(os.environ['HOME'], '.hla', cfs_filename)
    HLA_CFS_URL = os.environ.get('HLA_CFS_URL', None)

    if os.path.exists(src_home_csv):
        msg = "Creating lattice from home '%s'" % src_home_csv
        logger.info(msg)
        cfa.importSqliteDb(src_home_csv)
    elif os.environ.get('HLA_CFS_URL', None):
        msg = "Creating lattice from channel finder '%s'" % HLA_CFS_URL
        logger.info(msg)
        cfa.downloadCfs(HLA_CFS_URL, tagName='aphla.sys.*')
    elif conf.has(cfs_filename):
        src_pkg_csv = conf.filename(cfs_filename)
        msg = "Creating lattice from '%s'" % src_pkg_csv
        logger.info(msg)
        #cfa.importCsv(src_pkg_csv)
        cfa.importSqliteDb(src_pkg_csv)
    else:
        logger.error("Channel finder data are available, no '%s', no server" % 
                     cfs_filename)
        raise RuntimeError("Failed at loading cache file")

    #print(msg)
    for k in [('name', u'elemName'), 
              ('field', u'elemField'), 
              ('devname', u'devName'),
              ('family', u'elemType'), 
              ('handle', u'elemHandle'),
              ('index', u'elemIndex'), 
              ('se', u'elemPosition'),
              ('length', u'elemLength'),
              ('system', u'system')]:
        cfa.renameProperty(k[1], k[0])

    #tags = cfa.tags('aphla.sys.*')

    global _lat, _lattice_dict

    # should be 'aphla.sys.' + ['VSR', 'VLTB', 'VLTD1', 'VLTD2']
    logger.info("Initializing lattice according to the tags: %s" % HLA_TAG_SYS_PREFIX)

    for latname in ['SR', 'LTB', 'LTD1', 'LTD2']:
        lattag = HLA_TAG_SYS_PREFIX + '.' + latname
        logger.info("Initializing lattice %s (%s)" % (latname, lattag))
        _lattice_dict[latname] = createLattice(latname, cfa.rows, lattag,
                                               desc = cfa.source)

    orm_filename = ''
    if orm_filename and conf.has(orm_filename):
        #print("Using ORM:", conf.filename(orm_filename))
        _lattice_dict['SR'].ormdata = OrmData(conf.filename(orm_filename))
    else:
        logger.warning("No ORM '%s' found" % orm_filename)

    # a virtual bpm. its field is a "merge" of all bpms.
    bpms = _lattice_dict['SR'].getElementList('BPM')
    allbpm = merge(bpms, **{'virtual': 1, 'name': HLA_VBPM, 
                            'family': HLA_VFAMILY})
    _lattice_dict['SR'].insertElement(allbpm, groups=[HLA_VFAMILY])

    #
    # LTB 
    _lattice_dict['LTB'].loop = False
    _lattice_dict['LTD1'].loop = False
    #_lat = _lattice_dict['LTB']

    #
    # SR
    _lattice_dict['SR'].loop = True
    _lat = _lattice_dict['SR']

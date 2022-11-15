import sys, os
import os.path as osp
import numpy as np
from scipy import interpolate
from subprocess import Popen, PIPE
import re
import matplotlib.pylab as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

import pysdds

SAMPLE_RADIA_TEXT_KICKMAP_FILEPATH = '/home/yhidaka/hg_repos/tracy-vs-elegant/kickmaps/W90v5_pole80mm_finemesh_7m.txt'
SAMPLE_SDDS_KICKMAP_FILEPATH       = '/home/yhidaka/hg_repos/tracy-vs-elegant/kickmaps/W90v5_pole80mm_finemesh_7m.sdds'

AUTOGEN_RADIA_TEXT_KICKMAP_FILEPATH = '/home/yhidaka/hg_repos/tracy-vs-elegant/kickmaps/autogen.txt'
AUTOGEN_SDDS_KICKMAP_FILEPATH       = '/home/yhidaka/hg_repos/tracy-vs-elegant/kickmaps/autogen.sdds'

#----------------------------------------------------------------------
def load_Radia_text_file(filepath):
    """
    """

    f = open(filepath,'r')
    all_text = f.read()
    f.close()

    if '# Horizontal Kick [micro-rad]' in all_text:
        unit = 'urad'
    elif '# Horizontal Kick [T2m2]' in all_text:
        unit = 'T2m2'
    elif '# Horizontal 2nd Order Kick [T2m2]' in all_text:
        unit = 'T2m2'
    elif '# Total Horizontal 2nd Order Kick [T2m2]' in all_text:
        unit = 'T2m2'
    else:
        raise ValueError('Unexpected unit for kickmap')

    line_list = all_text.split('\n')
    nLines = len(line_list)

    START_line_numbers = [i for i in range(nLines)
                          if re.match('^START\s*$', line_list[i]) is not None]
    START_line_num = {'horiz': None, 'vert': None, 'longit': None}
    if len(START_line_numbers) == 2:
        START_line_num['horiz'], START_line_num['vert'] = START_line_numbers
    elif len(START_line_numbers) == 3:
        START_line_num['horiz'], START_line_num['vert'], \
            START_line_num['longit'] = START_line_numbers
    else:
        raise ValueError('The number of "START" lines in Radia file must be 2 or 3.')

    param_list = []
    for line in line_list:
        if not line.startswith('#'):
            param_list.append(float(line))
            if len(param_list) == 3:
                undulator_length, nh, nv = param_list
                nh = int(nh); nv = int(nv)
                hkick = np.zeros((nv,nh))
                vkick = np.zeros((nv,nh))
                xmat = np.zeros((nv,nh))
                ymat = np.zeros((nv,nh))
                break

    if START_line_num['longit'] is not None:
        zkick = np.zeros((nv,nh))
    else:
        zkick = None

    line = line_list[START_line_num['horiz']+1]
    x = [float(s) for s in line.split()]
    y = [0.0]*len(x)

    for i in range(nv):
        line = line_list[START_line_num['horiz']+2+i]
        split_line = line.split()
        y[i] = float(split_line[0])
        hkick[i,:] = [float(s) for s in split_line[1:]]
        xmat[i,:] = x
        ymat[i,:] = y[i]

        line = line_list[START_line_num['vert']+2+i]
        split_line = line.split()
        vkick[i,:] = [float(s) for s in split_line[1:]]

        if START_line_num['longit'] is not None:
            line = line_list[START_line_num['longit']+2+i]
            split_line = line.split()
            zkick[i,:] = [float(s) for s in split_line[1:]]

    return {'x': xmat, 'y': ymat, 'hkick': hkick, 'vkick': vkick, 'zkick': zkick,
            'unit': unit, 'undulator_length': undulator_length}

#----------------------------------------------------------------------
def load_SDDS_file(sdds_filepath):
    """"""

    _, column_dict = pysdds.printout(sdds_filepath,column_name_list=None)

    return column_dict

#----------------------------------------------------------------------
def load_SDDS_file_as_radia_dict(sdds_filepath, undulator_length=None):
    """"""

    sdds_dict = load_SDDS_file(sdds_filepath)
    nx, ny, radia_dict = convert_SDDS_vecs_to_Radia_format(sdds_dict)
    radia_dict['unit'] = 'T2m2'
    radia_dict['undulator_length'] = undulator_length

    return radia_dict, nx, ny

#----------------------------------------------------------------------
def convert_SDDS_vecs_to_Radia_format(sdds_dict):
    """
    Elegant SDDS kickmap file does NOT contain longitudinal table.
    """

    nx = np.unique(sdds_dict['x']).shape[0]
    ny = np.unique(sdds_dict['y']).shape[0]

    radia_x = np.flipud(sdds_dict['x'].reshape((ny,nx)))
    radia_y = np.flipud(sdds_dict['y'].reshape((ny,nx)))
    radia_hkick = np.flipud(sdds_dict['xpFactor'].reshape((ny,nx)))
    radia_vkick = np.flipud(sdds_dict['ypFactor'].reshape((ny,nx)))

    return nx, ny, {'x': radia_x, 'y': radia_y, 'hkick': radia_hkick,
                    'vkick': radia_vkick, 'zkick': None}

#----------------------------------------------------------------------
def convert_Radia_matrices_to_SDDS_format(radia_matrix_dict):
    """"""

    sdds_x = np.flipud(radia_matrix_dict['x']).ravel()
    sdds_y = np.flipud(radia_matrix_dict['y']).ravel()
    sdds_xpFactor = np.flipud(radia_matrix_dict['hkick']).ravel()
    sdds_ypFactor = np.flipud(radia_matrix_dict['vkick']).ravel()

    return {'x': sdds_x, 'y': sdds_y, 'hkick': sdds_xpFactor, 'vkick': sdds_ypFactor}

#----------------------------------------------------------------------
def check_Radia_SDDS_equality(Radia_filepath, sdds_filepath):
    """"""

    radia_dict = load_Radia_text_file(Radia_filepath)
    radia_dict = convert_Radia_matrices_to_SDDS_format(radia_dict)

    sdds_dict  = load_SDDS_file(sdds_filepath)

    if not np.all(radia_dict['x'] == sdds_dict['x']):
        print 'x vectors do not match.'
        return

    if not np.all(radia_dict['y'] == sdds_dict['y']):
        print 'y vectors do not match.'
        return

    if not np.all(radia_dict['hkick'] == sdds_dict['xpFactor']):
        print 'Horizontal kick vectors do not match'
        return

    if not np.all(radia_dict['vkick'] == sdds_dict['ypFactor']):
        print 'Vertical kick vectors do not match'
        return

    print 'The specified Radia text file and SDDS file data match.'

#----------------------------------------------------------------------
def compare_kickmap_file_equality(filepath1, file_format1,
                                  filepath2, file_format2,
                                  undulator_length=None, decimal=14):
    """"""

    if file_format1 == 'radia':
        radia_dict1 = load_Radia_text_file(filepath1)
    else:
        sdds_dict = load_SDDS_file(filepath1)
        nx, ny, radia_dict1 = convert_SDDS_vecs_to_Radia_format(sdds_dict)
        radia_dict1['unit'] = 'T2m2'
        radia_dict1['undulator_length'] = undulator_length

    if file_format2 == 'radia':
        radia_dict2 = load_Radia_text_file(filepath2)
    else:
        sdds_dict = load_SDDS_file(filepath2)
        nx, ny, radia_dict2 = convert_SDDS_vecs_to_Radia_format(sdds_dict)
        radia_dict2['unit'] = 'T2m2'
        radia_dict2['undulator_length'] = undulator_length

        radia_dict2, _, _ = load_SDDS_file_as_radia_dict(
            filepath2, undulator_length=undulator_length)

    compare_radia_dict_equality(radia_dict1, radia_dict2, decimal=decimal)

#----------------------------------------------------------------------
def compare_radia_dict_equality(radia_dict1, radia_dict2, decimal=14):
    """"""

    for k in radia_dict1.keys():
        if isinstance(radia_dict1[k], str):
            assert radia_dict1[k] == radia_dict2[k]
        elif isinstance(radia_dict1[k], (float, np.ndarray)):
            if (k == 'zkick') and \
               ((radia_dict1[k] is None) or (radia_dict2[k] is None)):
                continue
            np.testing.assert_almost_equal(radia_dict1[k], radia_dict2[k],
                                           decimal=decimal)
        elif radia_dict1[k] is None:
            if radia_dict2[k] is not None:
                assert k == 'zkick'
        else:
            raise ValueError('Unexpected type: '+str(radia_dict1[k]))


#----------------------------------------------------------------------
def generate_SDDS_kickmap_file_from_Radia_kickmap_file(
    Radia_kickmap_filepath, output_SDDS_filepath=None,
    design_energy_GeV=None, decimal=None):
    """
    The arguments "design_energy_GeV" and "decimal" are only needed
    when the input Radia file is NOT in the unit of T2m2. In this case,
    a temporary Radia file in the unit of T2m2 must be created before
    this function can convert the original Radia file into a SDDS kickmap
    file.
    """

    if output_SDDS_filepath is None:
        output_SDDS_filepath = Radia_kickmap_filepath.replace('.txt','')+'.sdds'

    radia_dict = load_Radia_text_file(Radia_kickmap_filepath)
    if radia_dict['unit'] != 'T2m2':
        if design_energy_GeV is None or decimal is None:
            raise ValueError('You must provide args "design_energy_GeV" and "decimal" for unit conversion of Radia kickmap file.')
        Radia_T2m2_filepath = 'temp_radia_T2m2.txt'
        change_Radia_kickmap_unit(Radia_kickmap_filepath, Radia_T2m2_filepath,
                                  'T2m2', design_energy_GeV, decimal=decimal)
        delete_temp_Radia_file = True
    else:
        Radia_T2m2_filepath = Radia_kickmap_filepath
        delete_temp_Radia_file = False

    temp_sdds_filepath = output_SDDS_filepath+'.unsorted'

    if os.getenv('HOST_ARCH') is None:
        os.environ['HOST_ARCH'] = 'linux-x86_64'

    p = Popen(['km2sdds','-input',Radia_T2m2_filepath,
               '-output',temp_sdds_filepath],stdout=PIPE,stderr=PIPE)
    out, err = p.communicate()
    if err:
        print 'ERROR:'
        print err
        sys.exit(1)

    p = Popen(['sddssort','-column=y,increasing', '-column=x,increasing',
               temp_sdds_filepath, output_SDDS_filepath])
    out, err = p.communicate()
    if err:
        print 'ERROR:'
        print err
        sys.exit(1)

    os.remove(temp_sdds_filepath)
    os.remove(temp_sdds_filepath+'.1')

    if delete_temp_Radia_file:
        os.remove(Radia_T2m2_filepath)

#----------------------------------------------------------------------
def change_Radia_kickmap_unit(input_Radia_filepath, output_Radia_filepath,
                              desired_unit, design_energy_GeV, decimal=5):
    """"""

    if desired_unit not in ('T2m2', 'urad'):
        raise ValueError('arg "desired_unit" must be either "T2m2" or "urad".')

    radia_dict = load_Radia_text_file(input_Radia_filepath)

    if radia_dict['unit'] == desired_unit:
        print 'Input Radia file "{0:s}" already has the desired unit.'.format(input_Radia_filepath)
    else:
        c0 = 2.99792458e8
        Brho = 1e9*design_energy_GeV/c0 # magnetic rigidity [T-m]
        if (radia_dict['unit'] == 'T2m2') and (desired_unit == 'urad'):
            radia_dict['hkick'] = radia_dict['hkick']/(Brho**2)*1e6
            radia_dict['vkick'] = radia_dict['vkick']/(Brho**2)*1e6
            radia_dict['unit'] = 'urad'
        elif (radia_dict['unit'] == 'urad') and (desired_unit == 'T2m2'):
            radia_dict['hkick'] = radia_dict['hkick']/1e6*(Brho**2)
            radia_dict['vkick'] = radia_dict['vkick']/1e6*(Brho**2)
            radia_dict['unit'] = 'T2m2'
        else:
            raise ValueError('Uexpected unit change: from "{0:s}" to "{1:s}"'.format(
                radia_dict['unit'], desired_unit))

    generate_Radia_kickmap_file(radia_dict, output_Radia_filepath,
                                decimal=decimal)

#----------------------------------------------------------------------
def zero_Radia_kickmap_file(input_Radia_filepath, output_Radia_filepath,
                            kick_plane_list, decimal=5):
    """"""

    radia_dict = load_Radia_text_file(input_Radia_filepath)

    radia_dict = zero_kick(radia_dict, kick_plane_list)

    generate_Radia_kickmap_file(radia_dict, output_Radia_filepath,
                                decimal=decimal)

#----------------------------------------------------------------------
def zero_kick(radia_dict, kick_plane_list):
    """"""

    for kick_plane in kick_plane_list:
        if kick_plane in ('h','hkick','horiz','horizontal','x'):
            radia_dict['hkick'] *= 0.0
        elif kick_plane in ('v','vkick','vert','vertical','y'):
            radia_dict['vkick'] *= 0.0
        elif kick_plane in ('z','zkick','longit','longitudinal'):
            radia_dict['zkick'] *= 0.0
        else:
            raise ValueError('Unexpected "kick_plane": {0:s}'.format(kick_plane))

    return radia_dict

#----------------------------------------------------------------------
def change_Radia_kickmap_length(input_Radia_filepath, output_Radia_filepath,
                                desired_length, decimal=5):
    """"""

    radia_dict = load_Radia_text_file(input_Radia_filepath)

    radia_dict['hkick'] *= desired_length/radia_dict['undulator_length']
    radia_dict['vkick'] *= desired_length/radia_dict['undulator_length']
    if radia_dict['zkick'] is not None:
        radia_dict['zkick'] *= desired_length/radia_dict['undulator_length']
    radia_dict['undulator_length'] = desired_length

    generate_Radia_kickmap_file(radia_dict, output_Radia_filepath,
                                decimal=decimal)

#----------------------------------------------------------------------
def _write_Radia_kickmap_file(fileobj, nx, ny, radia_dict, decimal=5):
    """"""

    if radia_dict['unit'] not in ('T2m2', 'urad'):
        raise ValueError('"unit" must be either "T2m2" or "urad".')
    else:
        unit = radia_dict['unit']

    f = fileobj

    x_line_str_format = ' '.join(['{{{0:d}: .{1:d}e}}'.format(i, decimal) for i in range(nx  )])
    line_str_format   = ' '.join(['{{{0:d}: .{1:d}e}}'.format(i, decimal) for i in range(nx+1)])

    f.write('# Undulator Length [m]\n')
    f.write(str(radia_dict['undulator_length'])+'\n')

    f.write('# Number of Horizontal Points\n')
    f.write(str(nx)+'\n')

    f.write('# Number of Vertical Points\n')
    f.write(str(ny)+'\n')

    table_indent = 1
    y_indent = decimal+8

    if unit == 'T2m2':
        f.write('# Horizontal 2nd Order Kick [T2m2]\n')
    elif unit == 'urad':
        f.write('# Horizontal Kick [micro-rad]\n')
    f.write('START\n')
    f.write(' '*table_indent+' '*y_indent+' '+x_line_str_format.format(*tuple(radia_dict['x'][0,:]))+'\n')
    for i in range(ny):
        data_list = [radia_dict['y'][i,0]] + list(radia_dict['hkick'][i,:])
        f.write(' '*table_indent       +' '+  line_str_format.format(*data_list)+'\n')

    if unit == 'T2m2':
        f.write('# Vertical 2nd Order Kick [T2m2]\n')
    elif unit == 'urad':
        f.write('# Vertical Kick [micro-rad]\n')
    f.write('START\n')
    f.write(' '*table_indent+' '*y_indent+' '+x_line_str_format.format(*tuple(radia_dict['x'][0,:]))+'\n')
    for i in range(ny):
        data_list = [radia_dict['y'][i,0]] + list(radia_dict['vkick'][i,:])
        f.write(' '*table_indent       +' '+  line_str_format.format(*data_list)+'\n')

    if radia_dict['zkick'] is not None:
        f.write('# Longitudinally Integrated Squared Transverse Magnetic Field [T2m]\n')
        f.write('START\n')
        f.write(' '*table_indent+' '*y_indent+' '+x_line_str_format.format(*tuple(radia_dict['x'][0,:]))+'\n')
        for i in range(ny):
            data_list = [radia_dict['y'][i,0]] + list(radia_dict['zkick'][i,:])
            f.write(' '*table_indent       +' '+  line_str_format.format(*data_list)+'\n')


#----------------------------------------------------------------------
def generate_Radia_kickmap_file(radia_dict, output_Radia_text_filepath, decimal=5):
    """"""

    ny, nx = radia_dict['x'].shape

    f = open(output_Radia_text_filepath,'w')

    f.write('# Auto-generated by pyeletra.utils.kickmap.generate_Radia_kickmap_file()\n')

    _write_Radia_kickmap_file(f, nx, ny, radia_dict, decimal=decimal)

    f.close()

#----------------------------------------------------------------------
def generate_Radia_kickmap_file_from_SDDS_kickmap_file(
    SDDS_kickmap_filepath, undulator_length, output_Radia_text_filepath=None,
    decimal=5):
    """"""

    if output_Radia_text_filepath is None:
        output_Radia_text_filepath = SDDS_kickmap_filepath.replace('.sdds','')+'.txt'

    radia_dict, nx, ny = load_SDDS_file_as_radia_dict(SDDS_kickmap_filepath,
                                                      undulator_length=undulator_length)

    f = open(output_Radia_text_filepath,'w')

    f.write('# Auto-generated by pyeletra.utils.kickmap.generate_Radia_kickmap_file_from_SDDS_kickmap_file()\n')
    f.write('# based on the SDDS kickmap file "'+SDDS_kickmap_filepath+'"\n')

    _write_Radia_kickmap_file(f, nx, ny, radia_dict, decimal=decimal)

    f.close()

#----------------------------------------------------------------------
def plot1d_kickmap(radia_kickmap_filepath, kick_plane, x=None, y=None,
                   plot=True):
    """
    Plot the kick [T2m2] or [micro-rad] vs.:
      1) x (if y is given a double value)
      2) y (if x is given a double value)
    """

    if (x is None) and (y is None):
        x = 0.0

    radia_dict = load_Radia_text_file(radia_kickmap_filepath)

    if kick_plane in ('h','hkick','horiz','horizontal','x'):
        z = radia_dict['hkick']
        ylabel = 'Horizontal Kick [{0:s}]'.format(radia_dict['unit'])
    elif kick_plane in ('v','vkick','vert','vertical','y'):
        z = radia_dict['vkick']
        ylabel = 'Vertical Kick [{0:s}]'.format(radia_dict['unit'])
    elif kick_plane in ('z','zkick','longit','longitudinal'):
        z = radia_dict['zkick']
        ylabel = 'Radiation'
    else:
        raise ValueError('Unexpected "kick_plane": {0:s}'.format(kick_plane))

    if plot:
        plt.figure()

    if x is None:
        xvec = np.sort(radia_dict['x'][0,:])
        xdata = xvec
        ydata = interpolate.griddata((radia_dict['x'].ravel(), radia_dict['y'].ravel()),
                                     z.ravel(),
                                     (xvec[None,:], np.array([y]*xvec.size)[None,:]),
                                     method='linear', fill_value=np.nan).ravel()
        if plot:
            plt.plot(xdata, ydata, 'b.-')
            plt.xlabel('x [m]')
    else:
        yvec = np.sort(radia_dict['y'][:,0])
        xdata = yvec
        ydata = interpolate.griddata((radia_dict['x'].ravel(), radia_dict['y'].ravel()),
                                     z.ravel(),
                                     (np.array([x]*yvec.size)[None,:], yvec[None,:]),
                                     method='linear', fill_value=np.nan).ravel()
        if plot:
            plt.plot(xdata, ydata, 'b.-')
            plt.xlabel('y [m]')

    if plot:
        plt.ylabel(ylabel)
        plt.grid(True)

    return xdata, ydata

#----------------------------------------------------------------------
def plot_contour_kickmap(radia_kickmap_filepath, kick_plane, axis_image=False):
    """
    Plot contour map of the kick [T2m2] or [micro-rad]
    """

    radia_dict = load_Radia_text_file(radia_kickmap_filepath)

    if kick_plane in ('h','hkick','horiz','horizontal','x'):
        z = radia_dict['hkick']
        default_title_str = 'Horizontal Kick [{0:s}]'.format(radia_dict['unit'])
    elif kick_plane in ('v','vkick','vert','vertical','y'):
        z = radia_dict['vkick']
        default_title_str = 'Vertical Kick [{0:s}]'.format(radia_dict['unit'])
    elif kick_plane in ('z','zkick','longit','longitudinal'):
        z = radia_dict['zkick']
        default_title_str = 'Radiation'
    else:
        raise ValueError('Unexpected "kick_plane": {0:s}'.format(kick_plane))

    plt.figure()
    plt.pcolor(radia_dict['x']*1e3, radia_dict['y']*1e3, z,
               cmap=cm.jet)
    plt.xlabel('x [mm]', fontsize=20)
    plt.ylabel('y [mm]', fontsize=20)
    plt.title(default_title_str)
    if axis_image:
        plt.axis('image')
    else:
        plt.axis('tight')
    cb = plt.colorbar()

#----------------------------------------------------------------------
def plot_wireframe_kickmap(radia_kickmap_filepath, kick_plane, title_str=''):
    """
    Plot contour map of the kick [T2m2] or [micro-rad]
    """

    radia_dict = load_Radia_text_file(radia_kickmap_filepath)

    if kick_plane in ('h','hkick','horiz','horizontal','x'):
        z = radia_dict['hkick']
        zlabel = 'Horizontal Kick [{0:s}]'.format(radia_dict['unit'])
    elif kick_plane in ('v','vkick','vert','vertical','y'):
        z = radia_dict['vkick']
        zlabel = 'Vertical Kick [{0:s}]'.format(radia_dict['unit'])
    elif kick_plane in ('z','zkick','longit','longitudinal'):
        z = radia_dict['zkick']
        zlabel = 'Radiation'
    else:
        raise ValueError('Unexpected "kick_plane": {0:s}'.format(kick_plane))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_wireframe(radia_dict['x']*1e3, radia_dict['y']*1e3, z)
    plt.xlabel('x [mm]', fontsize=20)
    plt.ylabel('y [mm]', fontsize=20)
    ax.set_zlabel(zlabel, fontsize=20)
    plt.title(title_str)

#----------------------------------------------------------------------
def plot_surface_kickmap(radia_kickmap_filepath, kick_plane, title_str=''):
    """
    Plot contour map of the kick [T2m2] or [micro-rad]
    """

    radia_dict = load_Radia_text_file(radia_kickmap_filepath)

    if kick_plane in ('h','hkick','horiz','horizontal','x'):
        z = radia_dict['hkick']
        zlabel = 'Horizontal Kick [{0:s}]'.format(radia_dict['unit'])
    elif kick_plane in ('v','vkick','vert','vertical','y'):
        z = radia_dict['vkick']
        zlabel = 'Vertical Kick [{0:s}]'.format(radia_dict['unit'])
    elif kick_plane in ('z','zkick','longit','longitudinal'):
        z = radia_dict['zkick']
        zlabel = 'Radiation'
    else:
        raise ValueError('Unexpected "kick_plane": {0:s}'.format(kick_plane))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(radia_dict['x']*1e3, radia_dict['y']*1e3, z,
                           rstride=1, cstride=1, linewidth=0, cmap=cm.jet,
                           shade=True)
    plt.xlabel('x [mm]', fontsize=20)
    plt.ylabel('y [mm]', fontsize=20)
    ax.set_zlabel(zlabel, fontsize=20)
    plt.title(title_str)
    fig.colorbar(surf, shrink=1., aspect=10)


if __name__ == '__main__':

    #load_Radia_text_file(SAMPLE_RADIA_TEXT_KICKMAP_FILEPATH)

    #check_Radia_SDDS_equality(SAMPLE_RADIA_TEXT_KICKMAP_FILEPATH,
                              #SAMPLE_SDDS_KICKMAP_FILEPATH)

    #convert_SDDS_vecs_to_Radia_format(load_SDDS_file(SAMPLE_SDDS_KICKMAP_FILEPATH))

    #generate_Radia_kickmap_file_from_SDDS_kickmap_file(
        #SAMPLE_SDDS_KICKMAP_FILEPATH, undulator_length=7.02,
        #output_Radia_text_filepath=AUTOGEN_RADIA_TEXT_KICKMAP_FILEPATH)
    #check_Radia_SDDS_equality(AUTOGEN_RADIA_TEXT_KICKMAP_FILEPATH,
                              #SAMPLE_SDDS_KICKMAP_FILEPATH)

    #generate_SDDS_kickmap_file_from_Radia_kickmap_file(
        #SAMPLE_RADIA_TEXT_KICKMAP_FILEPATH,
        #output_SDDS_filepath=AUTOGEN_SDDS_KICKMAP_FILEPATH)
    #check_Radia_SDDS_equality(SAMPLE_RADIA_TEXT_KICKMAP_FILEPATH,
                              #AUTOGEN_SDDS_KICKMAP_FILEPATH)

    #epu_no_cs_filepath = '/home/yhidaka/hg_repos/tracy-vs-elegant/kickmaps/epu49v2lvg11kickmap2pure.dat'
    #epu_with_cs_filepath = '/home/yhidaka/hg_repos/tracy-vs-elegant/kickmaps/epu49v2lvg11kickmapres.dat'
    #y_no_cs, yp_no_cs = plot1d_kickmap(epu_no_cs_filepath, 'v', x=0.0)
    #x_no_cs, xp_no_cs = plot1d_kickmap(epu_no_cs_filepath, 'h', y=0.0)
    #y_with_cs, yp_with_cs = plot1d_kickmap(epu_with_cs_filepath, 'v', x=0.0)
    #x_with_cs, xp_with_cs = plot1d_kickmap(epu_with_cs_filepath, 'h', y=0.0)
    ##
    #plt.figure()
    #plt.plot(y_no_cs, yp_no_cs, 'b.-', y_with_cs, yp_with_cs, 'r.-')
    #plt.legend(['w/o Current Strip', 'w/ Current strip'])
    #plt.xlabel('y [m]')
    #plt.ylabel('Vertical Kick [urad]')
    #plt.grid(True)
    #plt.figure()
    #plt.plot(x_no_cs, xp_no_cs, 'b.-', x_with_cs, xp_with_cs, 'r.-')
    #plt.legend(['w/o Current Strip', 'w/ Current strip'])
    #plt.xlabel('x [m]')
    #plt.ylabel('Horizontal Kick [urad]')
    #plt.grid(True)
    ##
    #plt.show()

    axis_image = False
    epu_no_cs_filepath = '/home/yhidaka/hg_repos/tracy-vs-elegant/kickmaps/epu49v2lvg11kickmap2pure.dat'
    epu_with_cs_filepath = '/home/yhidaka/hg_repos/tracy-vs-elegant/kickmaps/epu49v2lvg11kickmapres.dat'
    #
    #plot_contour_kickmap(epu_no_cs_filepath, 'h', axis_image=axis_image)
    #plot_contour_kickmap(epu_no_cs_filepath, 'v', axis_image=axis_image)
    #plot_contour_kickmap(epu_with_cs_filepath, 'h', axis_image=axis_image)
    #plot_contour_kickmap(epu_with_cs_filepath, 'v', axis_image=axis_image)
    #
    #plot_wireframe_kickmap(epu_no_cs_filepath, 'h', title_str='w/o CS')
    #plot_wireframe_kickmap(epu_no_cs_filepath, 'v', title_str='w/o CS')
    #plot_wireframe_kickmap(epu_with_cs_filepath, 'h', title_str='w/ CS')
    #plot_wireframe_kickmap(epu_with_cs_filepath, 'v', title_str='w/ CS')
    #
    plot_surface_kickmap(epu_no_cs_filepath, 'h', title_str='w/o CS')
    plot_surface_kickmap(epu_no_cs_filepath, 'v', title_str='w/o CS')
    plot_surface_kickmap(epu_with_cs_filepath, 'h', title_str='w/ CS')
    plot_surface_kickmap(epu_with_cs_filepath, 'v', title_str='w/ CS')
    #
    plt.show()

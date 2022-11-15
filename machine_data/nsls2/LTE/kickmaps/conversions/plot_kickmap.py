import sys
#sys.path.remove('/usr/lib/pymodules/python2.6') # This hack is needed on the NSLS2 cluster
# for some reason to load "mplot3d" from my home installation.
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pylab as plt
import matplotlib.gridspec as gridspec
import matplotlib.colorbar as mplcb
from matplotlib import cm
from matplotlib.backends.backend_pdf import PdfPages

from pyeletra.utils.kickmap import load_Radia_text_file

#----------------------------------------------------------------------
def plot(filepath, title=''):
    """"""

    km = load_Radia_text_file(kickmap_filepath)

    fig = plt.figure()
    gs = gridspec.GridSpec(1, 2, width_ratios=(15,1))
    ax, ax_colorbar = [fig.add_subplot(ax) for ax in gs]
    ax.set_axis_on(); ax_colorbar.set_axis_off()
    plt.sca(ax)
    pc = plt.pcolor(km['x']*1e3, km['y']*1e3, km['hkick'])
    plt.sca(ax_colorbar)
    cax, _ = mplcb.make_axes_gridspec(ax_colorbar, fraction=2.0, pad=0.0)
    plt.colorbar(pc, cax=cax)
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    ax.set_title(r'$\theta_x [\mu \mathrm{rad}]$', size='x-large')
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.95])

    fig = plt.figure()
    gs = gridspec.GridSpec(1, 2, width_ratios=(15,1))
    ax, ax_colorbar = [fig.add_subplot(ax) for ax in gs]
    ax.set_axis_on(); ax_colorbar.set_axis_off()
    plt.sca(ax)
    pc = plt.pcolor(km['x']*1e3, km['y']*1e3, km['vkick'])
    plt.sca(ax_colorbar)
    cax, _ = mplcb.make_axes_gridspec(ax_colorbar, fraction=2.0, pad=0.0)
    plt.colorbar(pc, cax=cax)
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    ax.set_title(r'$\theta_y [\mu \mathrm{rad}]$', size='x-large')
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.95])

    fig = plt.figure()
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0], projection='3d')
    _ = ax.plot_surface(km['x']*1e3, km['y']*1e3, km['hkick'],
                        linewidth=0, rstride=1, cstride=1, cmap=cm.jet)
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    ax.set_zlabel(r'$\theta_x [\mu \mathrm{rad}]$', size='x-large')
    ax.set_title(title)
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.95])

    fig = plt.figure()
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0], projection='3d')
    _ = ax.plot_surface(km['x']*1e3, km['y']*1e3, km['vkick'],
                        linewidth=0, rstride=1, cstride=1, cmap=cm.jet)
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    ax.set_zlabel(r'$\theta_y [\mu \mathrm{rad}]$', size='x-large')
    ax.set_title(title)
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.95])

    fig = plt.figure()
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0], projection='3d')
    _ = ax.plot_wireframe(km['x']*1e3, km['y']*1e3, km['hkick'])
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    ax.set_zlabel(r'$\theta_x [\mu \mathrm{rad}]$', size='x-large')
    ax.set_title(title)
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.95])

    fig = plt.figure()
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0], projection='3d')
    _ = ax.plot_wireframe(km['x']*1e3, km['y']*1e3, km['vkick'])
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    ax.set_zlabel(r'$\theta_y [\mu \mathrm{rad}]$', size='x-large')
    ax.set_title(title)
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.95])



    along_x_zero = (km['x'] == 0.0)
    along_y_zero = (km['y'] == 0.0)

    fig = plt.figure()
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0])
    ax.hold(True)
    ax.plot(km['y'][along_x_zero]*1e3, km['hkick'][along_x_zero], 'b.-',
            label=r'$\theta_x$')
    ax.plot(km['y'][along_x_zero]*1e3, km['vkick'][along_x_zero], 'r.-',
            label=r'$\theta_y$')
    ax.grid(True)
    ax.set_xlabel('y [mm] (x = 0)')
    ax.set_ylabel(r'Kick Angle $[\mu \mathrm{rad}]$', size='x-large')
    ax.set_title(title)
    ax.legend(loc='best')
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.95])

    fig = plt.figure()
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0])
    ax.hold(True)
    ax.plot(km['x'][along_y_zero]*1e3, km['hkick'][along_y_zero], 'b.-',
            label=r'$\theta_x$')
    ax.plot(km['x'][along_y_zero]*1e3, km['vkick'][along_y_zero], 'r.-',
            label=r'$\theta_y$')
    ax.grid(True)
    ax.set_xlabel('x [mm] (y = 0)')
    ax.set_ylabel(r'Kick Angle $[\mu \mathrm{rad}]$', size='x-large')
    ax.set_title(title)
    ax.legend(loc='best')
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.95])


if __name__ == '__main__':

    plt_show = False
    #case_indexes = range(3)
    #case_indexes = [3, 4]
    #case_indexes = [5,6,7,8]
    #case_indexes = [9, 10]
    case_indexes = [11,12,13,14,15,16]

    for case_index in case_indexes:

        if case_index == 0:
            kickmap_filepath = 'EPU105ESMv2LVG19PS14L2800mmKickMapRes_2o8m_urad.txt'
            pdf_filepath = 'kmplot_ESM_105_CS_14PS.pdf'
            plot(kickmap_filepath, title='ESM 105-mm w/ 14-PS Current Strips')
        elif case_index == 1:
            kickmap_filepath = 'EPU105ESMv2LVG19L2800mmKickMapRes_2o8m_urad.txt'
            pdf_filepath = 'kmplot_ESM_105_CS_allPS.pdf'
            plot(kickmap_filepath, title='ESM 105-mm w/ Full Current Strips')
        elif case_index == 2:
            kickmap_filepath = 'EPU105ESMv2LVG19L2800mmKickMap2Pure_2o8m_urad.txt'
            pdf_filepath = 'kmplot_ESM_105_CS_Off.pdf'
            plot(kickmap_filepath, title='ESM 105-mm without Current Strips')
        elif case_index == 3:
            kickmap_filepath = 'ESM_EPU57v2LVG16KickMap2Pure_1o4m_urad.txt'
            pdf_filepath = 'kmplot_ESM_57_CS_Off.pdf'
            plot(kickmap_filepath, title='ESM 57-mm without Current Strips')
        elif case_index == 4:
            kickmap_filepath = 'ESM_EPU57v2LVG16KickMapRes_1o4m_urad.txt'
            pdf_filepath = 'kmplot_ESM_57_CS_On.pdf'
            plot(kickmap_filepath, title='ESM 57-mm with Current Strips')
        elif case_index == 5:
            kickmap_filepath = 'EPU57v2LVG16KickMap2Pure_3o5m_urad.txt'
            pdf_filepath = 'kmplot_SIX_CS_All_Off.pdf'
            plot(kickmap_filepath, title='SIX without All Current Strips')
        elif case_index == 6:
            kickmap_filepath = 'EPU57v2LVG16KickMapRes_3o5m_urad.txt'
            pdf_filepath = 'kmplot_SIX_CS_All_On.pdf'
            plot(kickmap_filepath, title='SIX with All Current Strips')
        elif case_index == 7:
            kickmap_filepath = 'EPU57v2ModeParaP28_6G16v2KickMap2Pure_3o5m_urad.txt'
            pdf_filepath = 'kmplot_SIX_CS_Sub_Off.pdf'
            plot(kickmap_filepath, title='SIX without Subset of Current Strips')
        elif case_index == 8:
            kickmap_filepath = 'EPU57v2ModeParaP28_6G16v2KickMapRes_3o5m_urad.txt'
            pdf_filepath = 'kmplot_SIX_CS_Sub_On.pdf'
            plot(kickmap_filepath, title='SIX with Subset of Current Strips')
        elif case_index == 9:
            kickmap_filepath = 'EPU49v2LVG11KickMapRes_2o0m_urad.txt'
            pdf_filepath = 'kmplot_CSX_CS_All_On.pdf'
            plot(kickmap_filepath, title='CSX LV @ 11mm w/ Full Current Strips')
        elif case_index == 10:
            kickmap_filepath = 'EPU49v2LVG11KickMap2Pure_2o0m_urad.txt'
            pdf_filepath = 'kmplot_CSX_CS_All_Off.pdf'
            plot(kickmap_filepath, title='CSX LV @ 11mm w/o Current Strips')
        elif case_index == 11:
            kickmap_filepath = 'U20_asbuilt_g52_1o5m_urad.txt'
            pdf_filepath = 'kmplot_C03_C11_half.pdf'
            plot(kickmap_filepath, title='C03/C11 Half')
        elif case_index == 12:
            kickmap_filepath = 'U21NX_boostmag_1o5m_urad.txt'
            pdf_filepath = 'kmplot_C05_C17.pdf'
            plot(kickmap_filepath, title='C05/C17')
        elif case_index == 13:
            kickmap_filepath = 'U22_asbuilt_6m_g75mm_1o5m_urad.txt'
            pdf_filepath = 'kmplot_C10_half.pdf'
            plot(kickmap_filepath, title='C10 Half')
        elif case_index == 14:
            kickmap_filepath = 'U23L_asbuilt_g61_2o8m_urad.txt'
            pdf_filepath = 'kmplot_C04_C12.pdf'
            plot(kickmap_filepath, title='C04/C12')
        elif case_index == 15:
            kickmap_filepath = 'U23L_asbuilt_g57_2o8m_urad.txt'
            pdf_filepath = 'kmplot_C16.pdf'
            plot(kickmap_filepath, title='C16')
        elif case_index == 16:
            kickmap_filepath = 'X25MGU_1o0m_urad.txt'
            pdf_filepath = 'kmplot_C19.pdf'
            plot(kickmap_filepath, title='C19')
        else:
            raise ValueError('Unexpected case_index: {0:d}'.format(case_index))

        pp = PdfPages(pdf_filepath)
        for fig in plt.get_fignums():
            pp.savefig(figure=fig)
        pp.close()

        plt.close('all')

    if plt_show:
        plt.show()

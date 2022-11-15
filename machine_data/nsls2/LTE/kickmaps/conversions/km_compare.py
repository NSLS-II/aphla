import numpy as np
import matplotlib.pylab as plt
import matplotlib.gridspec as gridspec

from matplotlib.backends.backend_pdf import PdfPages

from pyeletra.utils.kickmap import load_Radia_text_file

#----------------------------------------------------------------------
def compare(km_filepaths, km_legends, title=''):
    """"""

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.hold(True)
    ax1.grid(True)
    ax1.set_xlabel('y [mm] (x = 0)')
    ax1.set_ylabel(r'$\theta_x [\mu \mathrm{rad}]$', size='x-large')
    ax1.set_title(title)

    fig = plt.figure()
    ax2 = fig.add_subplot(111)
    ax2.hold(True)
    ax2.grid(True)
    ax2.set_xlabel('y [mm] (x = 0)')
    ax2.set_ylabel(r'$\theta_y [\mu \mathrm{rad}]$', size='x-large')
    ax2.set_title(title)

    fig = plt.figure()
    ax3 = fig.add_subplot(111)
    ax3.hold(True)
    ax3.grid(True)
    ax3.set_xlabel('x [mm] (y = 0)')
    ax3.set_ylabel(r'$\theta_x [\mu \mathrm{rad}]$', size='x-large')
    ax3.set_title(title)

    fig = plt.figure()
    ax4 = fig.add_subplot(111)
    ax4.hold(True)
    ax4.grid(True)
    ax4.set_xlabel('x [mm] (y = 0)')
    ax4.set_ylabel(r'$\theta_y [\mu \mathrm{rad}]$', size='x-large')
    ax4.set_title(title)

    for km_fp, km_leg in zip(km_filepaths, km_legends):
        km = load_Radia_text_file(km_fp)

        along_x_zero = (km['x'] == 0.0)
        along_y_zero = (km['y'] == 0.0)

        ax1.plot(km['y'][along_x_zero]*1e3, km['hkick'][along_x_zero], '.-',
                 label=km_leg)
        ax2.plot(km['y'][along_x_zero]*1e3, km['vkick'][along_x_zero], '.-',
                 label=km_leg)
        ax3.plot(km['x'][along_y_zero]*1e3, km['hkick'][along_y_zero], '.-',
                 label=km_leg)
        ax4.plot(km['x'][along_y_zero]*1e3, km['vkick'][along_y_zero], '.-',
                 label=km_leg)

    for ax in [ax1,ax2,ax3,ax4]:
        plt.sca(ax)
        ylo, yhi = ax.get_ylim()
        if abs(yhi) < 1e-3: yhi =  1e-3
        if abs(ylo) < 1e-3: ylo = -1e-3
        ax.set_ylim((ylo, yhi))
        ax.legend(loc='best')
        plt.tight_layout()


if __name__ == '__main__':

    plt_show = True

    #case_indexes = range(2)
    #case_indexes = [5]
    case_indexes = [0]

    for case_index in case_indexes:

        if case_index == 0:
            km_filepaths = [
                'EPU105ESMv2LVG19L2800mmKickMap2Pure_2o8m_urad.txt',
                'EPU105ESMv2LVG19PS14L2800mmKickMapRes_2o8m_urad.txt',
                'EPU105ESMv2LVG19L2800mmKickMapRes_2o8m_urad.txt',
            ]
            km_legends = ['Without CS', 'With 14-PS CS', 'With Full CS']
            title = 'ESM 105-mm Kickmaps'
            pdf_filepath = 'km_comp_ESM_105.pdf'
        elif case_index == 1:
            km_filepaths = [
                'EPU105ESMv2LVG19PS14L2800mmKickMapRes_2o8m_urad.txt',
                'EPU105ESMv2LVG19L2800mmKickMapRes_2o8m_urad.txt',
            ]
            km_legends = ['With 14-PS CS', 'With Full CS']
            title = 'Kickmaps for ESM 105-mm with Current Strips'
            pdf_filepath = 'km_comp_ESM_105_AllCS_vs_14CS.pdf'

        elif case_index == 2:
            km_filepaths = [
                'EPU57v2LVG16KickMap2Pure.dat',
                'EPU57v2ModeParaP28_6G16v2KickMap2Pure.dat',
            ]
            km_legends = ['Old', 'New']
            title = 'SIX Kickmap w/o Current Strips'
            pdf_filepath = 'test.pdf'

        elif case_index == 3:
            km_filepaths = [
                'EPU57v2LVG16KickMap2Pure_3o5m_urad.txt',
                'EPU57v2ModeParaP28_6G16v2KickMap2Pure.dat',
            ]
            km_legends = ['Old', 'New']
            title = 'SIX Kickmap w/o Current Strips'
            pdf_filepath = 'km_comp_EPU57LVPure_old_vs_new.pdf'

        elif case_index == 4:
            km_filepaths = [
                'EPU57v2ModeParaP28_6G16v2KickMapRes_3o5m_urad.txt',
                'EPU57v2LVG16KickMapRes_3o5m_urad.txt',
            ]
            km_legends = ['With 14-PS CS', 'With Full CS']
            title = 'Kickmaps for 3.5-m SIX 57-mm with Current Strips'
            pdf_filepath = 'km_comp_1SIX_AllCS_vs_14CS.pdf'

        elif case_index == 5:
            km_filepaths = [
                'EPU49v2LVG11KickMap2Pure_2o0m_urad.txt',
                'EPU49v2LVG11KickMapRes_2o0m_urad.txt',
            ]
            km_legends = ['WithoutCS', 'With CS']
            title = 'Kickmaps for CSX EPU49 w/ and w/o Current Strips'
            pdf_filepath = 'km_comp_1CSX_EPU49_w_vs_wo_CS.pdf'

        else:
            raise ValueError('Unexpected case_index: {0:d}'.format(case_index))

        compare(km_filepaths, km_legends, title=title)

        pp = PdfPages(pdf_filepath)
        for fig in plt.get_fignums():
            pp.savefig(figure=fig)
        pp.close()

        #plt.close('all')

    if plt_show:
        plt.show()


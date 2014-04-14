#! /usr/bin/env python

"""TinkerUtils Package

This package contains all the utility files for aptinker.
"""

import numpy as np
from time import strftime, localtime

from PyQt4.QtCore import QSize
from PyQt4.QtGui import QMessageBox, QFont, QTextEdit

#----------------------------------------------------------------------
def datestr(time_in_seconds_from_Epoch):
    """"""

    frac_sec = time_in_seconds_from_Epoch - np.floor(time_in_seconds_from_Epoch)
    time_format = '%Y-%m-%d (%a) %H:%M:%S.' + '{0:.6f}'.format(frac_sec)[2:]

    return strftime(time_format, localtime(time_in_seconds_from_Epoch))

#----------------------------------------------------------------------
def datestr_ns(ioc_raw_timestamp_tuple):
    """"""

    seconds, nanoseconds = ioc_raw_timestamp_tuple

    if nanoseconds == -1:
        return 'None'

    time_format = '%Y-%m-%d (%a) %H:%M:%S.'
    str_upto_seconds = strftime(time_format, localtime(seconds))

    return str_upto_seconds + '{:d}'.format(nanoseconds)

#----------------------------------------------------------------------
def date_month_folder_str(time_in_seconds_from_Epoch):
    """"""

    time_format = '%Y-%m'
    return strftime(time_format, localtime(time_in_seconds_from_Epoch))

#----------------------------------------------------------------------
def date_snapshot_filename_str(time_in_seconds_from_Epoch, username):
    """"""

    frac_sec = time_in_seconds_from_Epoch - np.floor(time_in_seconds_from_Epoch)
    time_format = '%Y-%m-%d-%H-%M-%S.' + '{0:.6f}'.format(frac_sec)[2:]

    time_str = strftime(time_format, localtime(time_in_seconds_from_Epoch))

    return '{0}_{1}.h5'.format(username, time_str)

########################################################################
class SmartSizedMessageBox(QMessageBox):
    """
    Taken from the answer by Paul Etherton at

    http://stackoverflow.com/questions/2655354/how-to-allow-resizing-of-qmessagebox-in-pyqt4
    """

    #----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""

        super(SmartSizedMessageBox, self).__init__(*args, **kwargs)

    #----------------------------------------------------------------------
    def resizeEvent(self, event):
        """
        We only need to extend resizeEvent, not every event.
        """

        result = super(SmartSizedMessageBox, self).resizeEvent(event)

        f = QFont('Monospace')
        f.setPointSize(14)
        f.setStyleHint(QFont.TypeWriter)

        details_box = self.findChild(QTextEdit)
        details_box.setFont(f)
        fm = details_box.fontMetrics()
        text = details_box.property('plainText')
        lines = text.split('\n')
        rect = fm.boundingRect(lines[0])
        width  = int(rect.width()*1.5)
        height = int(rect.height()*len(lines)*1.5)
        if details_box is not None:
            details_box.setFixedSize(QSize(width, height))

        return result

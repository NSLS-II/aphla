from __future__ import print_function

from numpy import *
import commands

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def sdds2py(FileName,para_col,para_col_name):
    '''
    export data from sdds file (parameter or column) data to python data
    from sdds2py import *
    output=sdds2py(FileName,para_col,para_col_name)
    output=sdds2py('Tester0.twi','col','s')


    FileName: sdds format filename
    para_col: define the exported data, which is either para or col
    para_col_name: parameter or coloum name
    output is either a float (for para) or an array (for column data)
    '''

    cmd='sdds2stream -' +para_col+'='+ para_col_name + '  ' + FileName
    print(cmd)

    if para_col[0:3]=='par':
        value=commands.getoutput(cmd)
        if value[0:5]=='error':
            print(value)
        else:
            if is_number(value):
                value=float(value)
    elif para_col[0:3]=='col':
        col=commands.getoutput(cmd)
        if col[0:5]=='error':
            value=col
            print(col)
        else:
            value=array([i for i in col.split('\n')])
            if is_number(value[0]):
                value=array([float(i) for i in col.split('\n')])
    else:
        value='incorrect input'


    print(value)

    return value


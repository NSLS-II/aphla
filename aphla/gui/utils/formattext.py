import numpy as np
DEFAULT_TAB_WIDTH = len('\t'.expandtabs())

#----------------------------------------------------------------------
def whitespace_delimited_lines(numpy_2d_string_array, ljust=True,
                               equal_len=False):
    """"""
    
    try:
        nRows, nCols = numpy_2d_string_array.shape
    except:
        raise TypeError('First argument must be a 2D string numpy array.')
    
    max_str_width_list = _get_maxlen_list(numpy_2d_string_array)
    if equal_len:
        max_str_width = max(max_str_width_list)
        max_str_width_list = [max_str_width]*nCols
    
    formatted_line_list = [[] for i in range(nRows)]
    if ljust:
        for (i,row) in enumerate(numpy_2d_string_array):
            formatted_line_list[i] = ' '.join(
                [s.ljust(w) for (s,w) in zip(row,max_str_width_list)] )
    else:
        for (i,row) in enumerate(numpy_2d_string_array):
            formatted_line_list[i] = ' '.join(
                [s.rjust(w) for (s,w) in zip(row,max_str_width_list)] )
            
    return formatted_line_list
    
#----------------------------------------------------------------------
def _get_maxlen_list(numpy_2d_string_array):
    """Find maximum string length for each column"""

    maxlen_list = [len( max(a,key=len) )
                   for a in numpy_2d_string_array.transpose()]
    
    return maxlen_list
        
#----------------------------------------------------------------------
def tab_delimited_unformatted_lines(numpy_2d_string_array):
    """
    Good for Microsoft Excel pasting
    """

    try:
        nRows, nCols = numpy_2d_string_array.shape
    except:
        raise TypeError('First argument must be a 2D string numpy array.')

    formatted_line_list = [[] for i in range(nRows)]
    for (i,row) in enumerate(numpy_2d_string_array):
        formatted_line_list[i] = '\t'.join([s for s in row] )
            
    return formatted_line_list
    
#----------------------------------------------------------------------
def tab_delimited_formatted_lines(numpy_2d_string_array, 
        tab_width=DEFAULT_TAB_WIDTH, equal_len=False, always_tab_end=True,
        newline_end=True):
    """
    Looks well-formatted if pasted into a text editor
    """

    try:
        nRows, nCols = numpy_2d_string_array.shape
    except:
        raise TypeError('First argument must be a 2D string numpy array.')
    
    max_str_width_list = _get_maxlen_list(numpy_2d_string_array)
    if equal_len:
        max_str_width = max(max_str_width_list)
        max_str_width_list = [max_str_width]*nCols
    
    if newline_end:
        line_end_char = '\n'
    else:
        line_end_char = ''
        
    formatted_line_list = [[] for i in range(nRows)]
    for (i,row) in enumerate(numpy_2d_string_array):
        formatted_line_list[i] = ' '.join(
            [_tabjust(s,w,always_tab_end=always_tab_end) 
             for (s,w) in zip(row,max_str_width_list)] ) + line_end_char
            
    return formatted_line_list
    
#----------------------------------------------------------------------
def _tabexpanded_len(string, tab_width=DEFAULT_TAB_WIDTH):
    """"""
    
    return len(string.expandtabs(tab_width))
    
#----------------------------------------------------------------------
def _tabjust(string, maxlen, tab_width=DEFAULT_TAB_WIDTH, always_tab_end=True):
    """"""
    
    if always_tab_end:
        return string + '\t'*((max((maxlen-len(string)),1)-1)/tab_width+1)
    else:
        return string + '\t'*(((maxlen-len(string))*(len(string)<maxlen)-1)/tab_width+1)
    
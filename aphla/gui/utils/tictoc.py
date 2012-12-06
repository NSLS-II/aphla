import time

#----------------------------------------------------------------------
def tic():
    """"""
    
    return time.time()
    
#----------------------------------------------------------------------
def toc(tStart):
    """"""
    
    tEnd = time.time()
    
    elapsed_time = tEnd - tStart
    
    return elapsed_time


HLA FAQ (Frequently Asked Questions)
=====================================

- The element can have fields to read or set, where to find them ?

  Use the following command

  ::

    >>> CH = hla.getElements('HCOR')
    >>> CH.fields()
    ['status', 'x', 'value']
    >>> CH.x = 1e-6
    >>> print CH.x

- Why I can not find element ...

  Are you using the proper 

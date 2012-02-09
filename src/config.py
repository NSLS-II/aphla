qtapp = [] # A container for an instance of Qt.QApplication class.
# It is necessary to declare this variable here in the configuration
# file since an application that imports this config file can check
# whether there is already a running QApplication instance.
#
# Also note that an empty list is used here, instead of, for example,
# None. You cannot use None in this case for the purpose of communicating
# this variable across different modules. The reason is that None is
# an immutable value, whereas a list is mutable. If you use None, even
# after you make a change to the variable in one module, the change
# will not be reflected when accessed in a different module, i.e., you
# always get None.
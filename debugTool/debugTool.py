def debug_trace():
    # Sets a tracepoint in the Python debugger that works with Qt
    from PyQt4.QtCore import pyqtRemoveInputHook
    from pdb import set_trace
    pyqtRemoveInputHook()
    set_trace()

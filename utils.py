def set_ipdb_debugger():
    import sys
    import ipdb
    import traceback

    def info(t, value, tb):
        traceback.print_exception(t, value, tb)
        ipdb.pm()

    sys.excepthook = info

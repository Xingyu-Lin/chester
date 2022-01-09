def set_ipdb_debugger():
    import sys
    import ipdb
    import traceback

    def info(t, value, tb):
        if t == KeyboardInterrupt:
            traceback.print_exception(t, value, tb)
            return
        else:
            traceback.print_exception(t, value, tb)
            ipdb.pm()

    sys.excepthook = info

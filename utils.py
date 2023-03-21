import os
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

def rsync_code(remote_host, remote_dir):
    command = 'rsync -avzh --delete --include-from=\'./chester/rsync_include\' --exclude-from=\'./chester/rsync_exclude\' ./ ' + remote_host + ':' + remote_dir
    # print("Sync command: ", command)
    os.system(command)
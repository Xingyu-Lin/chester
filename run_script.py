import os
import os.path as osp
from chester import config
from chester.utils import rsync_code
import click

# Run script on remote machine
@click.command()
@click.argument('script', type=str)
@click.option('--mode', type=str, default='rll')
@click.option('--dry', is_flag=True)
def run_script(script, mode, dry):
    remote_dir = config.REMOTE_DIR[mode]
    rsync_code(remote_host=mode, remote_dir=remote_dir)
    command = "ssh {host} \'cd {remote_dir} && . ./prepare.sh && {script}\'".format(host=mode, remote_dir=remote_dir, script=script)
    if not dry:
        os.system(command)
    else:
        print(command)

if __name__ == '__main__':
    run_script()
import sys
import os
import argparse

sys.path.append('.')
from chester import config

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    parser.add_argument('folder', type=str)
    parser.add_argument('--dry', action='store_true', default=False)
    parser.add_argument('--bare', action='store_true', default=False)
    parser.add_argument('--ckpt', action='store_true', default=False)
    args = parser.parse_args()

    args.folder = args.folder.rstrip('/')
    local_dir = args.folder
    remote_data_dir = os.path.join(config.REMOTE_DIR[args.host], args.folder)
    # Check if remote folder exists and if not, create it
    command = """ssh {host} "mkdir -p {remote_data_dir}" """.format(
        host=args.host,
        remote_data_dir=remote_data_dir)
    if not args.dry:
        os.system(command)

    command = """rsync -avzh --delete --progress {local_dir} {host}:{remote_data_dir}""".format(
        host=args.host,
        remote_data_dir=remote_data_dir,
        local_dir=local_dir)
    if not args.ckpt:
        command += " --exclude '*.ckpt'" + " --exclude '*.pth'"
    if args.bare:
        command += """--mkdir --exclude '*.pkl' --exclude '*.png' --exclude '*.gif' --exclude '*.pth' --exclude '*.pt' --include '*.csv' --include '*.json' --exclude '*.ckpt' --exclude '*.pth'  --delete"""
    if args.dry:
        print(command)
    else:
        os.system(command)

# To use the command here, add "alias slurm='python {path_to_this_file}'" to .bashrc
# and then run
import os
import argparse


def get_args(cmd=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str)
    parser.add_argument('node', type=str)
    parser.add_argument('--mem', type=int, default=20)
    parser.add_argument('--dry', action='store_true')

    if cmd:
        args = parser.parse_args()
    else:
        args = parser.parse_args("")

    return args


args = get_args(True)

if args.node in ['0-25', '0-17', '0-33']:
    partition = 'long'
elif args.node in []:
    partition = 'short'
else:
    assert False, 'node not known!'

if args.command == 'salloc':
    time = '7-12:00:00' if partition == 'long' else 'short'
    command = f"salloc -t {time} -p {partition} --mem={args.mem}G -w autobot-{args.node}"
else:
    raise NotImplementedError

if args.dry:
    print(command)
else:
    os.system(command)

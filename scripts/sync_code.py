from chester.utils import rsync_code
from chester.config import REMOTE_DIR

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='rll', type=str)
    args = parser.parse_args()
    rsync_code(args.mode, REMOTE_DIR[args.mode])

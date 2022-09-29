import os
import sys
import shutil
import os.path as osp
import json
import time
import datetime
import dateutil.tz
import tempfile
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

LOG_OUTPUT_FORMATS = ['csv', 'tensorboard']


class KVWriter(object):
    def writekvs(self, kvs):
        raise NotImplementedError


class InstantWriter(object):
    def write_now(self, *args, **kwargs):
        raise NotImplementedError


class CSVOutputFormat(KVWriter):
    def __init__(self, filename):
        self.file = open(filename, 'w+t')
        self.keys = []
        self.sep = ','

    def writekvs(self, kvs, *args, **kwargs):
        # Add our current row to the history
        extra_keys = kvs.keys() - self.keys
        if extra_keys:
            self.keys.extend(extra_keys)
            self.file.seek(0)
            lines = self.file.readlines()
            self.file.seek(0)
            for (i, k) in enumerate(self.keys):
                if i > 0:
                    self.file.write(',')
                self.file.write(k)
            self.file.write('\n')
            for line in lines[1:]:
                self.file.write(line[:-1])
                self.file.write(self.sep * len(extra_keys))
                self.file.write('\n')
        for (i, k) in enumerate(self.keys):
            if i > 0:
                self.file.write(',')
            v = kvs.get(k)
            if v is not None:
                self.file.write(str(v))
        self.file.write('\n')
        self.file.flush()

    def close(self):
        self.file.close()


class TensorBoardOutputFormat(InstantWriter):
    """
    Dumps key/value pairs into TensorBoard's numeric format.
    """

    def __init__(self, log_dir):
        os.makedirs(log_dir, exist_ok=True)
        from torch.utils.tensorboard import SummaryWriter
        self.writer = SummaryWriter(log_dir)

    def get_loggable_tags(self, output, tags_to_skip=("time", "data_time"), add_mode=True, tag_name="train"):
        tags = {}
        for tag, val in output.items():
            if tag in tags_to_skip:
                continue
            if add_mode and "/" not in tag:
                tag = f"{tag_name}/{tag}"
            tags[tag] = val
        return tags

    def write_now(self, tags, n_iter, tag_name="train", *args, **kwargs):
        tags = self.get_loggable_tags(tags, tag_name=tag_name)
        for tag, val in tags.items():
            if isinstance(val, str):
                self.writer.add_text(tag, val, n_iter)
            elif np.isscalar(val) or val.size == 1:
                self.writer.add_scalar(tag, val, n_iter)
            else:
                if val.ndim == 2:
                    cmap = plt.get_cmap('jet')
                    val = cmap(val)[..., :3]
                assert val.ndim == 3, f"Image should have two dimension! You provide: {tag, val.shape}!"
                self.writer.add_image(tag, val, n_iter, dataformats='HWC')

    def close(self):
        self.writer.close()


class WandbOutputFormat(KVWriter):
    """
    Dumps key/value pairs into wandb's numeric format.
    """

    def __init__(self, dir):
        raise NotImplementedError

    def writekvs(self, kvs):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


def make_output_format(format, ev_dir, log_suffix=''):
    os.makedirs(ev_dir, exist_ok=True)
    if format == 'csv':
        return CSVOutputFormat(osp.join(ev_dir, 'progress%s.csv' % log_suffix))
    elif format == 'tensorboard':
        return TensorBoardOutputFormat(osp.join(ev_dir, 'tf_logs%s' % log_suffix))
    elif format == 'wandb':
        assert False
        return WandbOutputFormat()
    else:
        raise ValueError('Unknown format specified: %s' % (format,))


# ================================================================
# API
# ================================================================

def logkv(key, val):
    """
    Log a value of some diagnostic
    Call this once for each diagnostic quantity, each iteration
    If called many times, last value will be used.
    """
    ExpLogger.CURRENT.logkv(key, val)


def logkv_mean(key, val):
    """
    The same as logkv(), but if called many times, values averaged.
    """
    ExpLogger.CURRENT.logkv_mean(key, val)


def logkvs(d, *args, **kwargs):
    """
    Log a dictionary of key-value pairs
    """
    ExpLogger.CURRENT.logkvs(d, *args, **kwargs)


def dumpkvs():
    """
    Write all the diagnostics from the current iteration

    level: int. (see logger.py docs) If the global logger level is higher than
                the level argument here, don't print to stdout.
    """
    ExpLogger.CURRENT.dumpkvs()


def getkvs():
    return ExpLogger.CURRENT.name2val


def get_dir():
    """
    Get directory that log files are being written to.
    will be None if there is no output directory (i.e., if you didn't call start)
    """
    return ExpLogger.CURRENT.get_dir()


# ================================================================
# Backend
# ================================================================

class ExpLogger(object):
    CURRENT = None
    def __init__(self, dir, output_formats):
        self.name2val = defaultdict(float)  # values this iteration
        self.name2cnt = defaultdict(int)
        self.dir = dir
        self.output_formats = output_formats

    # Logging API, forwarded
    # ----------------------------------------
    def logkv(self, key, val):
        self.name2val[key] = val

    def logkvs(self, d, *args, **kwargs):
        for key, val in d.items():
            self.logkv(key, val)
        for fmt in self.output_formats:
            if isinstance(fmt, InstantWriter):
                fmt.write_now(d, *args, **kwargs)

    def logkv_mean(self, key, val):
        if val is None:
            self.name2val[key] = None
            return
        oldval, cnt = self.name2val[key], self.name2cnt[key]
        self.name2val[key] = oldval * cnt / (cnt + 1) + val / (cnt + 1)
        self.name2cnt[key] = cnt + 1

    def dumpkvs(self):
        # Will only dump for stdout and text log
        # wandb and tensorboard are dumped automatically
        for fmt in self.output_formats:
            if isinstance(fmt, KVWriter):
                fmt.writekvs(self.name2val)
        self.name2val.clear()
        self.name2cnt.clear()

    # Configuration
    # ----------------------------------------
    def get_dir(self):
        return self.dir

    def close(self):
        for fmt in self.output_formats:
            fmt.close()


def configure(dir=None, add_formats=None, exp_name=None):
    if dir is None:
        # Default exp name
        dir = osp.join(tempfile.gettempdir(),
                       datetime.datetime.now().strftime("chester-%Y-%m-%d-%H-%M-%S"))

    assert isinstance(dir, str)
    os.makedirs(dir, exist_ok=True)

    format_strs = LOG_OUTPUT_FORMATS
    if add_formats is not None:
        format_strs = format_strs + add_formats

    output_formats = [make_output_format(f, dir) for f in format_strs]
    ExpLogger.CURRENT = ExpLogger(dir=dir, output_formats=output_formats)
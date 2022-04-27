import os
import glob
import pickle
import time
from config import AUTOBOT_NODELIST
import psutil

stats_dir = '/project_data/ramanan/mengtial/nodestats'
queue_dir = '/tmp/chester_queue'
check_interval = 1
user_name = 'zixuanhu'


def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower() and user_name == proc.username():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def check_available_nodes():
    all_stats_path = glob.glob(stats_dir + '/*.pkl')
    stats_names = [p.split('/')[-1][:-4] for p in all_stats_path]
    all_stats = [pickle.load(open(p, 'rb')) for p in all_stats_path]
    available_nodes = {}
    for name, (sys_data, gpu_data) in zip(stats_names, all_stats):
        gpu_ids = []
        for i, data in enumerate(gpu_data):
            if len(data['procs']) == 0:
                # if data['mem_usage'] < 20:
                gpu_ids.append(i)
        if len(gpu_ids) > 0:
            available_nodes[name] = gpu_ids
    return available_nodes


if checkIfProcessRunning('remote_scheduler'):
    exit()
while 1:
    time.sleep(check_interval)

    # check jobs in the queue
    tasks = glob.glob('*')
    tasks_with_time = [(os.path.getmtime(t), t) for t in tasks]
    sorted_tasks = sorted(tasks_with_time)

    # check if any GPUs are available
    available_GPUs = check_available_nodes()  # [...(node_name, [available_gpu_id])...]

    for _, script in sorted_tasks:
        with open(script) as f:
            node_list = f.readline().rstrip()[10:].split(',')
        for node in node_list:
            real_node = 'autobot-' + node
            # TODO: add gpu num
            if real_node in available_GPUs:
                gpu_ids = available_GPUs[real_node]
                if len(gpu_ids) > 0:
                    env_command = f'CUDA_VISIBLE_DEVICES={gpu_ids[0]} '
                    os.system(f"ssh {real_node} \'nohup bash {script} &")  # TODO redirect output
                    os.system(f'rm {script}')
                    gpu_ids.pop(0)

import os
import glob
import pickle
import time
from chester import config
from datetime import datetime
check_interval = 10


def check_available_nodes():
    all_stats_path = glob.glob(config.GPU_STATE_DIR + '/*.pkl')
    stats_names = [p.split('/')[-1][:-4] for p in all_stats_path]
    all_stats = [pickle.load(open(p, 'rb')) for p in all_stats_path]
    available_nodes = {}
    for name, (sys_data, gpu_data) in zip(stats_names, all_stats):
        gpu_ids = []
        for i, data in enumerate(gpu_data):
            if len(data['procs']) == 0:  # GPU is available if no user process is found on the GPU
                # if data['mem_usage'] < 20:
                gpu_ids.append(i)
        if len(gpu_ids) > 0:
            available_nodes[name] = gpu_ids
    return available_nodes


while 1:
    # check jobs in the queue
    tasks = glob.glob(os.path.join(config.CHESTER_QUEUE_DIR, '*'))
    tasks_with_time = [(os.path.getmtime(t), t) for t in tasks if os.path.isfile(t)]
    sorted_tasks = sorted(tasks_with_time)
    if len(sorted_tasks) == 0:
        t = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        print(f"{t:} All jobs done!")
        break
    # check if any GPUs are available
    available_GPUs = check_available_nodes()  # Dictionary: {node_name, [available_gpu_id])...]

    for _, script in sorted_tasks:
        with open(script) as f:
            while True:  # Read header files
                line = f.readline()
                if line[0] != '#':
                    break
                header = line.split(' ')[0][1:]
                if header == 'nodelist':
                    node_list = line.rstrip()[10:].split(',')
                elif header == 'CHESTEROUT':
                    stdout_file = line.rstrip().split(' ')[1]
                elif header == 'CHESTERERR':
                    stderr_file = line.rstrip().split(' ')[1]
                elif header == 'CHESTERSCRIPT':
                    script_file = line.split(' ')[1]
        for node in node_list:
            real_node = 'autobot-' + node
            # TODO: add gpu num
            if real_node in available_GPUs:
                gpu_ids = available_GPUs[real_node]
                if len(gpu_ids) > 0:
                    env_command = f'CUDA_VISIBLE_DEVICES={gpu_ids[0]} '
                    # TODO print beautiful
                    command = f"ssh -q {real_node} \'{env_command} bash {script_file} </dev/null >{stdout_file} 2>{stderr_file} &\'"
                    # command = f"ssh -q {real_node} \'{env_command} python /home/xlin3/test.py </dev/null >{stdout_file} 2>{stderr_file} &\'"
                    rm_command = f'rm {script}'
                    print(command)
                    os.system(command)
                    print(rm_command)
                    os.system(rm_command)
                    gpu_ids.pop(0)
                    break
                else:
                    del available_GPUs[real_node]
    time.sleep(check_interval)
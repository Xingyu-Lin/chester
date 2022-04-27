
import os
import glob
import time

queue_dir = '/tmp/chester_queue'
check_interval = 1

def check_available_nodes()
while 1:
    time.sleep(check_interval)

    # check jobs in the queue
    tasks = glob.glob('*')
    tasks_with_time = [(os.path.getmtime(t), t) for t in tasks]
    sorted_tasks = sorted(tasks_with_time)

    # check if any GPUs are available
    available_GPUs = []  # [...(node_name, [available_gpu_id])...]
    for node, gpu_ids in available_GPUs:
        num_gpus = len(gpu_ids)
        for _, task in sorted_tasks:
            with open(task) as f:
                nodelist = f.readline()[:]
            # launch if node in node list, and num_gpus > request_gpus
            pass





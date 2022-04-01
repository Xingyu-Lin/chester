import os.path as osp
import os

# TODO change this before make it into a pip package
PROJECT_PATH = osp.abspath(osp.join(osp.dirname(__file__), '..'))

LOG_DIR = os.path.join(PROJECT_PATH, "data")

# Make sure to use absolute path
REMOTE_DIR = {
    'seuss': '/home/xlin3/Projects/dynamic_abstraction',
    'autobot': '/home/xlin3/Projects/dynamic_abstraction',
    'psc': '/home/xlin3/Projects/dynamic_abstraction',
    'nsh': '/home/xingyu/Projects/dynamic_abstraction',
    'yertle': '/home/xingyu/Projects/dynamic_abstraction',
    'satori': '/home/xingyu/Projects/dynamic_abstraction',
    'csail': '/data/vision/torralba/scratch/chuang/xingyu/Projects/dynamic_abstraction'
}

REMOTE_MOUNT_OPTION = {
    'seuss': '/usr/share/glvnd',
    'autobot': '/opt/',
    'satori': '/usr/share/glvnd',
    # 'psc': '/pylon5/ir5fpfp/xlin3/Projects/baselines_hrl/:/mnt',
}

REMOTE_LOG_DIR = {
    'seuss': os.path.join(REMOTE_DIR['seuss'], "data"),
    'autobot': os.path.join(REMOTE_DIR['autobot'], "data"),
    'satori': os.path.join(REMOTE_DIR['satori'], "data"),
    # 'psc': os.path.join(REMOTE_DIR['psc'], "data")
    'psc': os.path.join('/mnt', "data"),
}

# PSC: https://www.psc.edu/bridges/user-guide/running-jobs
# partition include [RM, RM-shared, LM, GPU]
# TODO change cpu-per-task based on the actual cpus needed (on psc)
# #SBATCH --exclude=compute-0-[7,11]
# Adding this will make the job to grab the whole gpu. #SBATCH --gres=gpu:1
REMOTE_HEADER = dict(seuss="""
#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --partition=GPU
#SBATCH --exclude=compute-0-[7,9]
#SBATCH --cpus-per-task=8
#SBATCH --time=480:00:00
#SBATCH --gres=gpu:2
#SBATCH --mem=80G
""".strip(), psc="""
#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --partition=RM
#SBATCH --ntasks-per-node=18
#SBATCH --time=48:00:00
#SBATCH --mem=64G
""".strip(), psc_gpu="""
#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --partition=GPU-shared
#SBATCH --gres=gpu:p100:1
#SBATCH --ntasks-per-node=4
#SBATCH --time=48:00:00
""".strip(),
                     # excluding RTX 3090 nodes for now since it does not work with the pytorch version and also the cuda version
                     # #SBATCH --exclude=autobot-0-[25,29,33,37]
                     # #SBATCH --exclude=autobot-0-9 - Disk seems to be not working on this node.
                     # #SBATCH --nodelist=autobot-0-33
                     autobot="""
#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --partition=short
#SBATCH --cpus-per-task=4
#SBATCH --exclude=autobot-0-[25,29,33,37]
#SBATCH --time=3-12:00:00
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
""".strip(), satori="""
#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --partition=long
#SBATCH --cpus-per-task=4
#SBATCH --time=3-12:00:00
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
""".strip())

# location of the singularity file related to the project
SIMG_DIR = {
    'seuss': '/home/xlin3/softgym_containers/softgymcontainer_v4.simg',
    'autobot': '/home/xlin3/softgym_containers/softgymcontainer_v3.simg',
    'satori': '/home/xingyu/softgym_containers/softgymcontainer_v3.simg',
    # 'psc': '$SCRATCH/containers/ubuntu-16.04-lts-rl.img',
    'psc': '/pylon5/ir5fpfp/xlin3/containers/ubuntu-16.04-lts-rl.img',

}
CUDA_MODULE = {
    'seuss': 'cuda-91',
    'autobot': 'cuda-11.1.1',
    'psc': 'cuda/9.0',
    'satori': 'cuda/10.2',

}
MODULES = {
    'seuss': ['singularity'],
    'autobot': ['singularity'],
    'satori': ['singularity'],
    'psc': ['singularity'],
}

DISABLE_SINGULARITY = True  # In case when autobot is malfunctioning

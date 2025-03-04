from shutil import copy2
from shutil import rmtree
import os
import re
import stat
import argparse
import math

parser = argparse.ArgumentParser(
    prog="launch.py",
    description="Le programme de lancement des benchmarks Idefix"
)
parser.add_argument('--max-cores', type=int)
parser.add_argument('--cores-per-node', type=int)
parser.add_argument('--problem-size', type=int)
parser.add_argument('--account', type=str)
args = parser.parse_args()

# Number of cores which we want to explore
minCores=1
maxCores=args.max_cores

#elementary 1D dimension
problemSize=args.problem_size

# coreperNode on the cluster we're running
coresPerNode=args.cores_per_node

#setup directory
setup="./setup"

#set number of cores
coreList=(int(2**i) for i in range(int(math.log2(minCores)), int(math.log2(maxCores)+0.5)+1))

for ncores in coreList:
    targetDir="%d"%ncores
    print("Doing %d cores setup"%ncores)
    if os.path.exists(targetDir):
        rmtree(targetDir)
    os.mkdir(targetDir)
    copy2(setup+"/idefix",targetDir)
    copy2(setup+"/definitions.hpp",targetDir)
    try:
        copy2(setup+"/bind.sh",targetDir)
    except:
        ## No binding, we do nothing
        pass

    # compute number of cores and node
    nodes=ncores//coresPerNode
    if nodes<1:
        nodes=1
        cores=ncores
    else:
        cores=coresPerNode

    print("%d nodes and %d cores"%(nodes,cores))

    # compute problem total resolution
    nx1=problemSize
    nx2=problemSize
    nx3=problemSize

    nproc1=1
    nproc2=1
    nproc3=1

    n2=int(math.log2(ncores))
    n2_3=n2//3
    mod = n2-n2_3*3

    nproc1=nproc1*2**(n2_3)
    nproc2=nproc2*2**(n2_3)
    nproc3=nproc3*2**(n2_3)

    if(mod>=1):
        nproc1=nproc1*2
    if(mod>=2):
        nproc2=nproc2*2

    print("nprocx1=%d, nprocx2=%d, nprocx3=%d"%(nproc1,nproc2,nproc3))

    inputOptions={}
    inputOptions['resx1']="%d"%(nproc1*problemSize)
    inputOptions['resx2']="%d"%(nproc2*problemSize)
    inputOptions['resx3']="%d"%(nproc3*problemSize)
    inputOptions['lx1']="%f"%(nproc1*1.0)
    inputOptions['lx2']="%f"%(nproc2*1.0)
    inputOptions['lx3']="%f"%(nproc3*1.0)

    # inifile substitution
    with open(setup+"/idefix.ini", 'r') as file:
        inifile = file.read()

    for key, val in inputOptions.items():
        inifile = re.sub(r'@{0}@'.format(key), val, inifile)

    with open(targetDir+"/idefix.ini",'w') as file:
        file.write(inifile)


    scriptOptions={}
    scriptOptions['nodes']="%d"%(nodes)
    scriptOptions['core']="%d"%(cores)
    scriptOptions['name']="benchmark-%d"%(ncores)
    scriptOptions['account']=args.account

    # inifile substitution
    with open(setup+"/script.slurm", 'r') as file:
        scriptfile = file.read()

    for key, val in scriptOptions.items():
        scriptfile = re.sub(r'@{0}@'.format(key), val, scriptfile)

    with open(targetDir+"/script.slurm",'w') as file:
        file.write(scriptfile)

    os.chmod(targetDir+"/script.slurm",stat.S_IRWXU)

    os.chdir(targetDir)
    os.system('sbatch ./script.slurm')
    os.chdir("..")

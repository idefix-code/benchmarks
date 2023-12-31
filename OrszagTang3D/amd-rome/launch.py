import numpy as np
from shutil import copy2
from shutil import rmtree
import os
import re
import stat

# Number of cores which we want to explore
minCores=1
maxCores=131072

#elementary 1D dimension
problemSize=16

# coreperNode (actually, threads per core...)
coresPerNode=4

#setup directory
setup="./setup"

#script name
scriptName="script.sh"

#command to launch scripts
launcher="ccc_msub"

#set number of cores
coreList=(2**(np.arange(np.log2(minCores),np.log2(maxCores)+1))).astype(int)

for ncores in coreList:
    targetDir="%d"%ncores
    print("Doing %d cores setup"%ncores)
    if os.path.exists(targetDir):
        rmtree(targetDir)
    os.mkdir(targetDir)
    copy2(setup+"/idefix",targetDir)
    copy2(setup+"/definitions.hpp",targetDir)

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

    n2=int(np.log2(ncores))
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
    scriptOptions['nodes']="%d"%(nodes)  # here nodes=MPI procs
    scriptOptions['core']="%d"%(cores)   # here cores=OPENMP Threads
    scriptOptions['name']="benchmark-%d"%(ncores)

    # inifile substitution
    with open(scriptName, 'r') as file:
        scriptfile = file.read()

    for key, val in scriptOptions.items():
        scriptfile = re.sub(r'@{0}@'.format(key), val, scriptfile)

    with open(targetDir+"/"+scriptName,'w') as file:
        file.write(scriptfile)

    os.chmod(targetDir+"/"+scriptName, stat.S_IRWXU)

    os.chdir(targetDir)
    os.system(launcher+ " ./" + scriptName)
    os.chdir("..")

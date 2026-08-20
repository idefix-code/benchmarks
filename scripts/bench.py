#!/usr/bin/env python3
###############################################################################
# Author : Marc Coiffier
# Author : Geoffroy Lesur (CNRS / IPAG)
# Author : Sébastien Valat (CNRS / IPAG)
###############################################################################

# Note : This is a rewrite of ./launch.py

###############################################################################
import os
import re
import json
import math
import stat
import shutil
import argparse
import datetime
import subprocess
import contextlib

###############################################################################
@contextlib.contextmanager
def jump_in_dir(path):
    '''
    Change current working dir for the given directoy for what is inside the
    with statement.
    '''
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)

###############################################################################
class BenchBase:
    '''
    Base class to implement all the bench steps.
    '''
    def __init__(self, args):
        # Number of cores which we want to explore
        self.min_cores = 1
        self.max_cores = args.max_cores

        #elementary 1D dimension
        self.problem_size = args.problem_size

        # coreperNode on the cluster we're running
        self.cores_per_node = args.cores_per_node

        #setup directory
        self.setup = args.build_directory

        # run directory
        self.run_directory = args.run_directory

        #directory of the cluster we use
        self.clusters_path = os.path.dirname(__file__)+"/../clusters/"
        self.cluster = self.clusters_path + args.cluster
        self.cluster_name = args.cluster

        #set number of cores
        self.core_list = [int(2**i) for i in range(int(math.log2(self.min_cores)), int(math.log2(self.max_cores)+0.5)+1)]

        # account
        self.account = args.account

        # scheduler
        self.scheduler = self.get_scheduler()

        # print
        self.print_infos()

    def gen_infos(self) -> list:
        '''
        Generate the information of the run to be displayed or dumped into the result DAT file.
        '''
        # build lines
        lines = [
            "-----------------------------------------------------",
            f"cluster_name   : {self.cluster_name}",
            f"account        : {self.account}",
            f"scheduler      : {self.scheduler}",
            "-----------------------------------------------------",
            f"cores          : {self.min_cores} .. {self.max_cores}",
            f"cores_per_node : {self.cores_per_node}",
            f"problem_size   : {self.problem_size}",
            f"core_list      : " + ', '.join([str(i) for i in self.core_list]),
            "-----------------------------------------------------",
            f"setup          : {self.setup}",
            f"run_directory  : {self.run_directory}",
            "-----------------------------------------------------",
        ]

        # ok
        return lines

    def print_infos(self) -> None:
        '''
        Print the run information prior to exacution.
        '''
        for line in self.gen_infos():
            print(line)
        print("")

    def get_scheduler(self) -> str:
        '''
        Guess the scheduler in use on the cluster base on the extention of the job template.
        '''
        # check
        if os.path.exists(self.cluster + '/script.slurm'):
            return 'slurm'
        elif os.path.exists(self.cluster + '/script.oar'):
            return 'oar'
        elif os.path.exists(self.cluster + '/script.sh'):
            return 'sh'
        else:
            raise Exception(f"Unknown scheduler for the given cluster {self.cluster}, cannot find not 'script.slurm', nor 'script.oar', nor 'script.sh' !")

    def gen_rundir_path(self, ncores: int, date: str = datetime.datetime.today().strftime('%Y-%m-%d')) -> str:
        '''
        Generate the path where to put the job and the results.
        '''
        # gen dir
        target_dir = f"{self.run_directory}/{date}/{self.problem_size}/{ncores}"
        return target_dir

    def gen_job_filename(self) -> str:
        '''
        Generate the write filename depending on the job scheduler in use (slurm or OAR).
        '''
        if self.scheduler == "slurm":
            return 'script.slurm'
        elif self.scheduler == "oar":
            return 'script.oar'
        elif self.scheduler == "sh":
            return 'script.sh'
        else:
            raise Exception(f"Invalid job schedulter : {self.scheduler}")

    def apply_template_on_file(self, outputFile: str, inputFile: str, inputOptions: dict) -> None:
        '''
        Apply the dictionnary values into the given template to generate the output file.
        '''
        # load file
        with open(inputFile, 'r') as file:
            inifile = file.read()

        # substitiute
        for key, val in inputOptions.items():
            inifile = re.sub(f'@{key}@', val, inifile)

        # store
        with open(outputFile,'w') as file:
            file.write(inifile)

###############################################################################
class BenchJobGenerator(BenchBase):
    '''
    Implement the job generation base on the templates from the given cluster.
    '''
    def __init__(self, args):
        super().__init__(args)

    def gen_all_jobs(self) -> None:
        '''
        Generate the jobs for all the selected number of core/GPU.
        '''
        for ncores in self.core_list:
            self.gen_job(ncores)
            print("")

    def gen_job(self, ncores: int) -> None:
        '''
        Generate a single job with the given number of core/GPU.
        '''
        # gen dir
        targetDir = self.gen_rundir_path(ncores)

        # log
        print(f"-- Generating {ncores} cores setup")

        # recrete dir
        if os.path.exists(targetDir):
            shutil.rmtree(targetDir)
        os.makedirs(targetDir)

        # copy files in
        print("---- Copying 'idefix'")
        shutil.copy2(self.setup+"/idefix", targetDir)
        print("---- Copying 'definition.hpp'")
        shutil.copy2(self.setup+"/definitions.hpp",targetDir)

        # handle option bind script
        bind_script = self.cluster+"/bind.sh"
        if os.path.exists(bind_script):
            print("---- Copying 'bind.sh'")
            shutil.copy2(bind_script, targetDir)

        # compute number of cores and node
        nodes=ncores//self.cores_per_node

        # fix & log
        if nodes<1:
            nodes=1
            cores=ncores
        else:
            cores=self.cores_per_node
        print("---- %d nodes and %d cores"%(nodes,cores))

        # get ini params
        print("---- Generating 'idefix.ini'")
        iniParams = self.gen_ini_params(self.problem_size, ncores)
        self.apply_template_on_file(targetDir+"/idefix.ini", self.setup+"/idefix.ini", iniParams)

        # gen job file
        print(f"---- Generating '{self.gen_job_filename()}'")
        jobParams = self.gen_job_params(nodes, cores, ncores)
        self.apply_template_on_file(targetDir + "/" + self.gen_job_filename(), self.cluster + "/" + self.gen_job_filename(), jobParams)
        os.chmod(targetDir + "/" + self.gen_job_filename(),stat.S_IRWXU)

    def gen_job_params(self, nodes:int, cores:int, ncores: int) -> dict:
        '''
        Generate the parameters to inject in the job script file.
        '''
        scriptOptions={}
        scriptOptions['nodes']="%d"%(nodes)
        scriptOptions['core']="%d"%(cores)
        scriptOptions['name']="idefix-bench-%d"%(ncores)
        scriptOptions['account']=self.account
        return scriptOptions

    def gen_ini_params(self, problemSize: int, ncores:int) -> dict:
        '''
        Generate the parameters to inject into the idefix INI file.
        '''
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

        print("---- nprocx1=%d, nprocx2=%d, nprocx3=%d"%(nproc1,nproc2,nproc3))

        inputOptions={}
        inputOptions['resx1']="%d"%(nproc1*problemSize)
        inputOptions['resx2']="%d"%(nproc2*problemSize)
        inputOptions['resx3']="%d"%(nproc3*problemSize)
        inputOptions['lx1']="%f"%(nproc1*1.0)
        inputOptions['lx2']="%f"%(nproc2*1.0)
        inputOptions['lx3']="%f"%(nproc3*1.0)

        # ok
        return inputOptions

###############################################################################
class BenchJobSubmitter(BenchBase):
    '''
    Once the jobs have been generated thay can be launched automatically by using this class.
    '''
    def __init__(self, args):
        super().__init__(args)

    def launch_all_jobs(self) -> None:
        '''
        Launch all the jobs.
        '''
        for ncores in self.core_list:
            self.launch_job(ncores)
            print("")

    def launch_job(self, ncores: int) -> None:
        '''
        Launch the job for the given number of core/GPU.
        '''
        # get dir
        targetDir = self.gen_rundir_path(ncores)

        # log
        print(f"-- Launching {targetDir}/{self.gen_job_filename()}")

        # jump in
        with jump_in_dir(targetDir):
            if self.scheduler == "slurm":
                subprocess.run(['sbatch', f'./{self.gen_job_filename()}'], shell=False, check=True)
            elif self.scheduler == "oar":
                subprocess.run(['oarsub', '-S', f'./{self.gen_job_filename()}'], shell=False, check=True)
            elif self.scheduler == "sh":
                subprocess.run(['bash', f'./{self.gen_job_filename()}'], shell=False, check=True)
            else:
                raise Exception(f"Invalid job schedulter : {self.scheduler}")

###############################################################################
class BenchJobExtractor(BenchBase):
    '''
    Once the run has been finished, this command can be used to extract the performance from
    the idefix log file and produce the summary files and plot.
    '''
    def __init__(self, args):
        super().__init__(args)

    def extract_all_infos(self, date: str, plot: bool = False) -> None:
        '''
        Extract all infos and generate the global scaling summary.
        '''
        # vars
        db = {}

        # gen summary for each run
        for ncores in self.core_list:
            db[ncores] = self.extract_infos(ncores, date)
            print("")

        # gen summary.json
        target_dir = f"{self.run_directory}/{date}/{self.problem_size}"
        fname_json = os.path.join(target_dir, "summary.json")
        print(f"-- Generate {fname_json}")
        with open(fname_json, "w") as fp:
            json.dump(db, fp=fp, indent='\t')
        print("")

        # gen raw summary.dat
        fname_dat = os.path.join(target_dir, "summary.dat")
        print(f"-- Generate {fname_dat}")
        with open(fname_dat, "w") as fp:
            for line in self.gen_infos():
                fp.write(f"# {line}\n")
            fp.write("#\n")
            fp.write("#Cores\tcell_updates_per_s\n")
            for key, value in db.items():
                fp.write(f"{key}\t{value['performance']}\n")
            print("")

        # gen gnuplot file
        fname_gnuplot = os.path.join(target_dir, "summary.gnuplot")
        self.gen_gnuplot_scaling_script(fname_gnuplot)
        print("")

        # run gnuplot and generate PDF
        if plot:
            with jump_in_dir(target_dir):
                print("-- Plotting scalability")
                subprocess.run("gnuplot summary.gnuplot", shell=True, check=True)

    def gen_gnuplot_scaling_script(self,gnuplot_file: str):
        '''
        Generate the gnuplot script to render the scaling plot.
        '''
        # gen
        print(f"-- Generate {gnuplot_file}")

        # gen lines
        lines = [
            '#!/usr/bin/env gnuplot',
            'set term pdf',
            'set output "summary.pdf"',
            f'set title "Idefix {self.problem_size}x{self.problem_size}x{self.problem_size} scaling on {self.cluster_name}"',
            'set xlabel "Cores"',
            'set ylabel "Performance (cell update/seconds)"',
            'set key off',
            'set grid',
            'set logscale x 2',
            'set yrange [0:]',
            'plot "summary.dat" u 1:2 w lp',
        ]

        # dump
        with open(gnuplot_file, "w") as fp:
            for line in lines:
                fp.write(f"{line}\n")

    def extract_infos(self, ncores:int, date: str) -> None:
        '''
        Extract the info for the given run.
        '''
        # gen dir
        targetDir = self.gen_rundir_path(ncores, date=date)    
        fname = os.path.join(targetDir, "summary.json")
        print(f"-- Generate {fname}")

        # store out
        result = {
            "date": date,
            "cores_pre_node": self.cores_per_node,
            "ncores": ncores,
            "cluster": self.cluster_name,
            "problem_size": self.problem_size
        }

        # get dir
        targetDir = self.gen_rundir_path(ncores, date=date)

        # load log
        with open(targetDir + "/idefix.0.log", 'r') as fp:
            lines = fp.readlines()

        # build regexps
        infos = {
            "idefix_version": re.compile(r"\s*Idefix version (.+)"),
            "kokkos_version": re.compile(r"\s*Built against Kokkos (.+)"),
            "running_node_0": re.compile(r"\s*Running on (.+)"),
            "gpu_model": re.compile(r"\s*Kokkos::Cuda\[ [0-9]+ \] (.+) : Selected"),
            "performance": re.compile(r"\s*Main: Perfs are (.+) cell updates/second"),
        }

        # parse
        for line in lines:
            for key, info in infos.items():
                if info.match(line):
                    result[key] = info.search(line).group(1)

        # some cast
        result['performance'] = float(result['performance'])

        # save it
        with open(fname, "w") as fp:
            json.dump(result, fp=fp, indent='\t')

        # ok
        return result

###############################################################################
class BenchIdefixBuilder:
    '''
    This class implement the building of Idefix on the requested cluster.
    '''
    def __init__(self, args):
        # config
        self.cluster_name = args.cluster
        self.commit_id = args.commit

        # workdir
        cluster_dir = self.cluster_name.replace('/','-')
        self.workdir = os.path.abspath(f"./idefix")
        self.source_dir = os.path.abspath(f"./idefix/{self.commit_id}")
        self.build_dir = os.path.abspath(f"./idefix/{self.commit_id}/build-{cluster_dir}")
        self.cluster_dir = os.path.abspath(f"./clusters/{self.cluster_name}")
        self.setup_dir = os.path.abspath(f"./OrszagTang3D/setup/")

    def idefix_build(self) -> None:
        '''
        Build idefix for the given cluster.
        '''
        self.git_clone_or_checkout()
        self.configure_and_build()

    def git_clone_or_checkout(self):
        '''
        Clone the sources or update them.
        '''

        # clone or checkout
        if os.path.exists(self.source_dir):
            with jump_in_dir(self.source_dir):
                subprocess.run(['git', 'pull'], shell=False, check=True)
                subprocess.run(['git', 'checkout', self.commit_id], shell=False, check=True)
                subprocess.run(['git', 'submodule', 'update', '--init'], shell=False, check=True)
        else:
            os.makedirs(self.workdir, exist_ok=True)
            subprocess.run(['git', 'clone', '-b', self.commit_id, '--recurse-submodules', 'https://github.com/idefix-code/idefix.git', self.source_dir], shell=False, check=True)

    def configure_and_build(self):
        '''
        Configure and compile Idefix for the current cluster.
        '''
        # jump in and build
        os.makedirs(self.build_dir, exist_ok=True)
        with jump_in_dir(self.build_dir):
            shutil.copy2(f"{self.setup_dir}/definitions.hpp", ".")
            shutil.copy2(f"{self.setup_dir}/CMakeLists.txt", ".")
            shutil.copy2(f"{self.setup_dir}/idefix.ini", ".")
            shutil.copy2(f"{self.setup_dir}/setup.cpp", ".")
            subprocess.run(["bash", "-c", f"set -e; source {self.cluster_dir}/env.sh; cmake $IDEFIX_FLAGS '{self.source_dir}' --fresh; make -j4"], shell=False, check=True)

###############################################################################
def main():
    '''
    Main entry point.
    '''

    # build parser
    parser = argparse.ArgumentParser(
        prog="bench.py",
        description="Generate, launch and extract the Idefix benchmarks"
    )

    # common options
    parser.add_argument('--max-cores', type=int, default=1)
    parser.add_argument('--cores-per-node', type=int, default=1)
    parser.add_argument('--problem-size', type=int, default=64)
    parser.add_argument('--account', type=str, default='default')
    parser.add_argument('--cluster', type=str, required=True)
    parser.add_argument('--build-directory', type=str, default='./idefix/@commit@/build-@cluster@')
    parser.add_argument('--run-directory', type=str, default='./runs/@commit@/@cluster@')
    parser.add_argument("--commit", type=str, help="The commit, tag or branch to build for.", default='master')

    # build sub parser
    subparsers = parser.add_subparsers(dest="command")

    # add 'gen' command
    cmd_gen = subparsers.add_parser('gen', help="Generate the jobs directories to be ready to run.")
    cmd_run = subparsers.add_parser('run', help="Run the jobs on the cluster (need to have generated them before).")
    cmd_extract = subparsers.add_parser('extract', help="Generate the final summary data file from the run.")
    cmd_extract.add_argument('--date', type=str, default=datetime.datetime.today().strftime('%Y-%m-%d'), help="Parmit to extract the data from another date.")
    cmd_extract.add_argument('--plot', action='store_true', help="Render the plottings with gnuplot.")
    cmd_build = subparsers.add_parser('build', help="Clone and build Idefix for the cluster.")

    # parse
    args = parser.parse_args()

    # replace
    cluster_dir = args.cluster.replace('/', '-')
    args.build_directory = args.build_directory.replace('@commit@', args.commit).replace('@cluster@', cluster_dir)
    args.run_directory = args.run_directory.replace('@commit@', args.commit).replace('@cluster@', cluster_dir)

    # run
    if args.command == 'gen':
        bench = BenchJobGenerator(args)
        bench.gen_all_jobs()
    elif args.command == 'run':
        bench = BenchJobSubmitter(args)
        bench.launch_all_jobs()
    elif args.command == 'extract':
        bench = BenchJobExtractor(args)
        bench.extract_all_infos(args.date, args.plot)
    elif args.command == 'build':
        bench = BenchIdefixBuilder(args)
        bench.idefix_build()
    else:
        raise Exception(f"Invalid command : {args.command}")

###############################################################################
if __name__ == "__main__":
    main()

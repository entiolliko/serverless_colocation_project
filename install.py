#!/usr/bin/env python3

import argparse
import os
import subprocess

parser = argparse.ArgumentParser(description="Install dependencies.")
parser.add_argument('--venv', metavar='DIR', type=str, default="python-venv", help='destination of local Python virtual environment')
parser.add_argument('--python-path', metavar='DIR', type=str, default="python3", help='Path to local Python installation.')
parser.add_argument("--with-pypapi", action="store_true", default=False)
args = parser.parse_args()

def execute(cmd, cwd=None):
    ret = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=cwd
    )
    if ret.returncode:
        raise RuntimeError(
            "Running {} failed!\n Output: {}".format(cmd, ret.stdout.decode("utf-8"))
        )
    return ret.stdout.decode("utf-8")

env_dir=args.venv

if not os.path.exists(env_dir):
    print("Creating Python virtualenv at {}".format(env_dir))
    execute(f"{args.python_path} -mvenv {env_dir}")
    execute(". {}/bin/activate && pip install --upgrade pip".format(env_dir))
else:
    print("Using existing Python virtualenv at {}".format(env_dir))

print("Install Python dependencies with pip")
execute(". {}/bin/activate && pip3 install -r requirements.txt --upgrade".format(env_dir))

# print("Update typing-extensions (resolving bug with mypy)")
# execute(". {}/bin/activate && pip3 install typing-extensions --upgrade".format(env_dir))

if args.with_pypapi:
    print("Build and install pypapi")
    cur_dir = os.getcwd()
    os.chdir(os.path.join(os.path.join("src/performance_counters", "third_party"), "pypapi"))
    execute(". ../../../../{}/bin/activate && pip3 install -r requirements.txt".format(env_dir))
    execute(". ../../../../{}/bin/activate && python3 setup.py install".format(env_dir))
    # execute(". ../../../{}/bin/activate && python3 pypapi/papi_build.py".format(env_dir))
    os.chdir(cur_dir)

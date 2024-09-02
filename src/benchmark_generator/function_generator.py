import sys
import json
import code_composer
import requirements_composer
import input_composer
import os
import datetime
import subprocess

def execute(cmd, cwd=None):
    ret = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=cwd
    )
    if ret.returncode:
        raise RuntimeError(
            "Running {} failed!\n Output: {}".format(cmd, ret.stdout.decode("utf-8"))
        )
    return ret.stdout.decode("utf-8")

def generate_function_from_config(config, folder_name, suffix):
    # Generate directory for benchmark
    path_to_benchmark = "generated_code/{}".format(folder_name)
    if not os.path.exists(path_to_benchmark):
        os.makedirs(path_to_benchmark)

    # Push code to benchmarks/600.generated/610.generated/python/function.py
    with open(path_to_benchmark + f"/function_{suffix}.py", "w+") as code_file:
        code = code_composer.compose(config)
        code_file.write(code)

    execute("isort " + path_to_benchmark.replace(" ", "\ ") + f"/function_{suffix}.py")

    # Push requirements to benchmarks/600.generated/610.generated/python/requirements.txt
    # with open(path_to_benchmark + f"/requirements_{suffix}.txt", "w+") as requirements_file:
    #    requirements = requirements_composer.compose(config.items())
    #    print("Req: " + requirements)
    #   requirements_file.write(requirements)

    # Create input.py file
    # with open(path_to_benchmark + f"/input_{suffix}.py", "w+") as input_file:
    #   code = input_composer.compose(config.items())
    #   input_file.write(code)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Missing argument, path to config")

    with open(sys.argv[1]) as config_file:
        config = json.load(config_file)
    
    curr_time = datetime.datetime.now()
    generate_function_from_config(config, curr_time)

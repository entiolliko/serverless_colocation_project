import os

def load_benchmark_code(benchmark_name, language="python"):
    current_dir = os.getcwd()
    path_to_code = os.path.join(current_dir, "src/benchmark_generator/functions", benchmark_name, language, "function.py" if language == "python" else "sth.js")
    if os.path.exists(path_to_code):
        with open(path_to_code, "r") as source_file:
            source_code = source_file.read()
            [_, after_test] = source_code.split("#test")
            [_, after_import] = after_test.split("#import")
            [import_part, after_parameter_fun] = after_import.split("#parameter_fun")
            [parameter_fun_part, after_function] = after_parameter_fun.split("#function")
            [function_part, after_create_cfg] = after_function.split("#create_cfg")
            [create_cfg, run_part] = after_create_cfg.split("#run")
            return {
                "import": import_part,
                "parameter_fun": parameter_fun_part,
                "function": function_part,
                "create_cfg": create_cfg,
                "run": run_part
            }
    return {
                "import": "",
                "parameter_fun": "",
                "function": "",
                "create_cfg": "",
                "run": ""
            }

def intend(body):
    new_body = ""
    for line in body.splitlines():
        new_body += "\n\t" + line
    return new_body

def compose(config_c):
    code = ""
    config = config_c.items()
    benchmarks_list = {benchmark for (benchmark, benchmark_config) in config}

    # load code of benchmarks
    code_maps = {
        benchmark_name: load_benchmark_code(benchmark_name) for benchmark_name in benchmarks_list
    }

    # add imports TODO: Update the code here
    for code_map in code_maps.values():
       code += code_map["import"] + "\n"
    #code += "import numpy as np\nimport time\nimport uuid\nimport os\nimport speedtest\nimport operator\n"
    code += "import sys\nsys.path.append(\"src/performance_counters\")\nimport papirunner\n"

    #add functions
    for code_map in code_maps.values():
        code += code_map["function"] + "\n"

    #add fill functions
    for code_map in code_maps.values():
        code += code_map["parameter_fun"] + "\n"
    
    code += "\ndef fill_function(cfg):\n"
    #add fill of benchmarks
    fill_function = "result = {}\n"
    for (number, (benchmark_name, benchmark_config)) in enumerate(config):
        fill_function += "config = " + str(benchmark_config) + "\n"
        fill_function += code_maps[benchmark_name]["create_cfg"] + "\n"

    code += intend(fill_function)
    code += "\n"

    code += "\ndef handler(cfg):\n"
    #add invoke of benchmarks
    handler_function = "result = {}\n"
    for (number, (benchmark_name, benchmark_config)) in enumerate(config):
        handler_function += code_maps[benchmark_name]["run"] + "\n"

    code += intend(handler_function) + "\n"
    
    #TODO: Add the call to the papi runner with the function handler and save the results in the csv file to create the dataset fo the counters
    main_fun = "if __name__ == \"__main__\":"     
    cfg = "cfg = {\"workload\": {}, \"network\" :{}, \"function_input\" : {}, \"readFile\": {}, \"disc\": {}, \"writeFile\": {}, \"memory\": {}}\n"
    body = f"papi_config_path = sys.argv[1]\n{cfg}"
    main_fun += intend(body)
    code += main_fun + intend("fill_function(cfg)\npapirunner.measure_function(handler, cfg, papi_config_path)") + "\n"
    
    return code

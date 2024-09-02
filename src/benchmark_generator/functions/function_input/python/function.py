#test
config = {
    "output_size": 100
}
cfg = {}
result = {}
#import
import uuid
#parameter_fun
def create_parameters_function_input(config, cfg):
    number_of_entries = config.get("output_size")
    cfg["function_input"]["output_size"] = number_of_entries 
#function
def fill_dict(dict_to_fill, cfg):
    number_of_entries = cfg["function_input"]["output_size"]
    for i in range(number_of_entries):
        dict_to_fill[str(uuid.uuid1())] = str(uuid.uuid1())
#create_cfg
create_parameters_function_input(config, cfg)
#run
fill_dict(result, cfg)

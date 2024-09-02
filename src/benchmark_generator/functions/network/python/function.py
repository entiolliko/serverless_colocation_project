#test
config = {}
cfg = {}
#import
import speedtest
#parameter_fun
def create_parameters_network(config, cfg):
    use = config.get("use")
    cfg["network"]["use"] = use
#function
def test_network(cfg):
    if cfg["network"]["use"] : s = speedtest.Speedtest()
#create_cfg
create_parameters_network(config, cfg)
#run
test_network(cfg)


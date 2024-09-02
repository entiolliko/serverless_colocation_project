README

Instructions:
python install.py
. python-venv/bin/activate
This should create the penv in the project which you can use to run the  

To run the code for the config in src/papi-experiment/config you can use the following command:
sudo python-venv/bin/python src/papi-experiment/papi_experiment.py 
This will generate the graphs as per the experiments specified in the config file.

NOTE: 
1. If you want to use the features Config_1/2/3/4 as discussed with Lucas you shouldn't change the list and order of the papi counters in the configu file. If you want to try other PAPI counters use DEFAULT as the feature type.   
2. Make sure your pc is able to collect the papi counters you want to use
3. The papi-experiment directory does not create the dataset on disk. If you want to save the dataset on disk as individual python files use the following command:
python src/benchmark_generator/data_generator.py

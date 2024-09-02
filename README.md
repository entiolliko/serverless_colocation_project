# README

## Setup Instructions

1. Install the required dependencies:
   ```bash
   python install.py
   ```

2. Activate the virtual environment:
   ```bash
   . python-venv/bin/activate
   ```
   This will create and activate the virtual environment (`penv`) in the project, which you can use to run the code.

## Running the Experiment

To execute the code using the configuration located in `src/papi-experiment/config`, use the following command:

```bash
sudo python-venv/bin/python src/papi-experiment/papi_experiment.py
```

This command will generate graphs based on the experiments specified in the configuration file.

## Notes

1. **Feature Configuration**:
   - If you want to use the `Config_1/2/3/4` features (as discussed with Lucas), **do not change** the list or order of the PAPI counters in the configuration file.
   - If you want to experiment with other PAPI counters, set the feature type to `DEFAULT`.

2. **PAPI Counters**:
   - Ensure that your machine is capable of collecting the PAPI counters you intend to use.

3. **Saving Datasets**:
   - The `papi-experiment` directory does **not** save the dataset on disk by default.
   - If you want to save the dataset as individual Python files, use the following command:
     ```bash
     python src/benchmark_generator/data_generator.py
     ```

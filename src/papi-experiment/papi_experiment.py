import argparse
import time
import random
import multiprocessing
import numpy as np
import json

from papi_measurement import papi_handler, sample_run_handler, check_supported_events
from utils import *



class PapiExperiment():
    def __init__(self, config):
        self.config = config
        

    def run_papi_handler(self, data):
        print("Running using MP Pool")
        pool = multiprocessing.Pool()
        results = pool.map(papi_handler, data)
        print("The MP Pool has finished running")
        return results


    def run_sample_run_handler(self, data):
        pool = multiprocessing.Pool()
        results = pool.map(sample_run_handler, data)
        return results


    def gather_papi_counters(self, data):
        results = self.run_papi_handler(data)
        random.shuffle(results)
        id_res_map = {}
        for res in results:
            id_res_map[res["ID"]] = res["res"]
        return id_res_map 

    
    def select_furthest_vectors(self, data, num_of_funs):
        selected_index = [random.choice(range(data.shape[0]))]
    
        while len(selected_index) < num_of_funs:
            curr_anchor = np.mean(data[selected_index], axis=0)
            distances = np.linalg.norm(data - curr_anchor, axis=1)  # Distance calculation
            sorted_indices = np.argsort(distances)[::-1]  # Sort by distance in descending order

            # Find the first index in the sorted list that is not already in selected_index
            for index in sorted_indices:
                if index not in selected_index:
                    selected_index.append(index)
                    break
                
        # while len(set(selected_index)) < num_of_
        assert num_of_funs == len(selected_index), "Not enough functions"
        assert len(set(selected_index)) == num_of_funs, "Not unique functions"

        return selected_index

    def perform_pca(self, data, n_components):
        
        min_vals = np.min(data, axis=0)
        max_vals = np.max(data, axis=0)

        range_vals = max_vals - min_vals

        # Replace any zeros in the range with ones to avoid division by zero
        range_vals[range_vals == 0] = 1

        normalized_data = (data - min_vals) / range_vals
        data_mean = np.mean(normalized_data, axis=0)
        centered_data = normalized_data - data_mean
        covariance_matrix = np.cov(centered_data, rowvar=False)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
        sorted_indices = np.argsort(eigenvalues)[::-1]
        sorted_eigenvectors = eigenvectors[:, sorted_indices]

        if n_components != -1:
            sorted_eigenvectors = sorted_eigenvectors[:, :n_components]

        return np.dot(centered_data, sorted_eigenvectors)


    def random_selection(self, id_2_counters, num_of_funs):
        fun_ids = list(id_2_counters.keys())
        random_ids = random.sample(fun_ids, num_of_funs)
        return random_ids


    def pca_selection(self, data, num_of_funs, n_components):
        transformed_data = self.perform_pca(data, n_components)
        return self.select_furthest_vectors(transformed_data, num_of_funs)


    def min_max_normalization_selection(self, data, num_of_funs):
        min_vals = np.min(data, axis=0)
        max_vals = np.max(data, axis=0)

        range_vals = max_vals - min_vals

        # Replace any zeros in the range with ones to avoid division by zero
        range_vals[range_vals == 0] = 1

        normalized_data = (data - min_vals) / range_vals
        return self.select_furthest_vectors(normalized_data, num_of_funs)


    def standardization_selection(self, vectors, num_of_funs):
        print(vectors.shape)
        means = np.mean(vectors, axis=0)
        std_devs = np.std(vectors, axis=0)

        std_devs[std_devs == 0] = 1

        vectors = (vectors - means) / std_devs
        return self.select_furthest_vectors(vectors, num_of_funs)


    def get_features(self, id_2_counters, feature_type):
        features = np.array([value for key, value in id_2_counters.items()])
        if feature_type == "DEFAULT":
            return features
        
        num_of_funs = features.shape[0]
        features_cnf1 = features[:, 0] / features[:, 1]
        features_cnf1 = features_cnf1.reshape((num_of_funs, 1))
        assert features_cnf1.shape == (num_of_funs, 1)
        if feature_type == "CONFIG_1":
            return features_cnf1
        
        features_cnf2 = features[:, 2] / features[:, 3]
        features_cnf2 = np.concatenate((features_cnf1, features_cnf2.reshape((num_of_funs, 1))), axis=1)
        assert features_cnf2.shape == (num_of_funs, 2)
        if feature_type == "CONFIG_2":
            return features_cnf2
        
        features_cnf3 = features[:, 6] / features[:, 1]
        features_cnf3 = np.concatenate((features_cnf2, features_cnf3.reshape((num_of_funs, 1))), axis=1)
        assert features_cnf3.shape == (num_of_funs, 3)
        if feature_type == "CONFIG_3":
            return features_cnf3
        
        features_cnf4 = features[:, 4] / features[:, 5]
        features_cnf4 = np.concatenate((features_cnf3, features_cnf4.reshape((num_of_funs, 1))), axis=1)
        assert features_cnf4.shape == (num_of_funs, 4)
        if feature_type == "CONFIG_4":
            return features_cnf4
        
        raise ValueError("No valid value for feature type: " + feature_type)


    def collect_similar_functions(self, id_2_counters, num_of_funs, config, feature_type):
        selection_criteria = config["type"]
        features = self.get_features(id_2_counters, feature_type)

        if selection_criteria == "random":
            return self.random_selection(id_2_counters, num_of_funs)
        elif selection_criteria == "pca":
            return self.pca_selection(features, num_of_funs, config["n_components"])
        elif selection_criteria == "min_max_normalization":
            return self.min_max_normalization_selection(features, num_of_funs)                   
        elif selection_criteria == "standardization":
            return self.standardization_selection(features, num_of_funs)
        else:
            raise NameError("The selection criteria: " + selection_criteria + " doesn't exist")


    def run_configuration(self, exp_config, input, id_2_counters, feature_type):
        print("Running config: " + str(exp_config))
        group_size = self.config["group_size"]
        sample_run_repetitions = self.config["sample_run_repetitions"]
    
        id_2_config = {}
        for i in input:
            id_2_config[i["ID"]] = i["config"]
        
        
        print("Selecting the function which are not similar to colocate")
        selected_fun_ids_to_run = self.collect_similar_functions(id_2_counters, group_size, exp_config, feature_type)

        selected_map = []
        for fun_id in selected_fun_ids_to_run:
            selected_map.append({"ID": fun_id , "config" : id_2_config[fun_id]})

        print("Measuring time to run the subset of functions in parallel")
        start_time = time.time()
        for i in range(sample_run_repetitions):
            self.run_sample_run_handler(selected_map)
        end_time = time.time()
        return (end_time - start_time) / sample_run_repetitions


    def run_experiment(self):
        num_of_funs = self.config["num_of_funs"]

        print("Gathering papi counters")
        input = generate_input(num_of_funs)
        temp_input = [(elem, self.config["papi_events"]) for elem in input]
        id_2_counters = self.gather_papi_counters(temp_input)
        
        # # Plain counters
        # data = self.get_features(id_2_counters, "DEFAULT")
        # tsne_plot_colored(data, 0, "fp_ins_tsne", "t-SNE plot of vectors colored by FP instructions")
        # tsne_plot_colored(data, 1, "tot_ins_tsne", "t-SNE plot of vectors colored by TOT instructions")
        # tsne_plot_colored(data, 4, "l1_dca_tsne", "t-SNE plot of vectors colored by L1 DCA")
        # 
        # # Plain counters
        # data = self.get_features(id_2_counters, "CONFIG_4")
        # tsne_plot_colored(data, 0, "fp_d_tot_tsne", "t-SNE plot of vectors colored by FP / TOT INS")
        # tsne_plot_colored(data, 1, "br_msp_d_ins_tsne", "t-SNE plot of vectors colored by BR MSP / BR INS")
        # tsne_plot_colored(data, 2, "vec_d_tot_ins_tsne", "t-SNE plot of vectors colored by VEC / TOT instructions")
        # tsne_plot_colored(data, 3, "l1_dca_d_tca_ins_tsne", "t-SNE plot of vectors colored by L1 DCA / TCA instructions")
        

        plot_titles = []
        means = []    
        stds = []
        for exp in self.config["experiment"]:
            plot_titles.append(exp["plot_title"])
            measurements = []
            for _ in range(self.config["experiment_repetition"]):
                measurements.append(self.run_configuration(exp, input, id_2_counters, self.config["feature_type"]))
            mean, std = get_mean_var(measurements)
            means.append(mean)
            stds.append(std)
        
        print(plot_titles, means, stds)
        plot_bar_graph(plot_titles, means, stds, self.config["file_name"])


            
def main(config_path):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
        
        for experiment_config in config["environments"]:
            experiment = PapiExperiment(experiment_config)
            experiment.run_experiment()
            
        
    except FileNotFoundError:
        print(f"Error: The file '{config_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{config_path}' is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")    


if __name__ == "__main__":
    # print(check_supported_events())

    parser = argparse.ArgumentParser()
    parser.add_argument('--config-path', default="src/papi-experiment/configs/example.json", type=str, help="Path to the config file.")
    args = parser.parse_args()
    
    main(args.config_path)
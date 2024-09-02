import os
import random
import numpy as np
from scipy.stats import burr
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

C = 11.652
D = 0.221
SCALE = 107.083
NUMBER_OF_DATAPOINTS = 250 
possible_values = list(range(1, 11000001, 1000))
operators = ["+", "-", "*", "/"]


def generate_input(size):
    res = []
    for i in range(size):
        path_to_file = f"temp/temp_file_{i}.npy"
        config = {"writeFile": {}, "disc": {}, "function_input": {}, "memory": {}, "workload": {}, "network": {}}
        config["writeFile"]["path_to_file"] = path_to_file
        config["disc"]["path_to_file"] = path_to_file
    
        workload_iterations = random.choice(possible_values)
        workload_operator  = random.choice(operators)
        memory_size = int(burr.rvs(C, D, SCALE, size=2)[0] / 5)

        config["disc"]["block_size"] = memory_size 
        config["function_input"]["output_size"] = memory_size
        config["memory"]["size_in_bytes"] = memory_size
        config["workload"]["array_size"] = memory_size 
        config["writeFile"]["block_size"] = memory_size
        config["workload"]["type"] = "float32"
        config["workload"]["iterations"] = workload_iterations
        config["workload"]["operator"] = workload_operator
        config["network"]["use"] = workload_operator  = random.choice([False, True])
                    
        res.append({"ID":i, "config": config})

    return res


def clean_temp_folder():
    directory_path = "temp/"
    try:
        if not os.path.exists(directory_path):
            print(f"Directory '{directory_path}' does not exist.")
            return

        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isfile(file_path):
                os.remove(file_path)
                
        print("All temp files removed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")


def get_mean_var(data):
    if len(data) == 0:
        raise ValueError("The list of numbers is empty.")
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return mean, variance


def plot_bar_graph(selection_criteria, means, std, file_name):
    assert len(means) == len(std)
    
    N = len(means)
    
    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars

    fig, ax = plt.subplots()
    rects = ax.bar(ind, means, width, color='r', yerr=std)

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Time')
    ax.set_title('Time by selection criteria')
    ax.set_xticks(ind)# + width / 2)
    ax.set_xticklabels(selection_criteria)

    # ax.legend((rects), ('Experiment'))

    def autolabel(rects):
        """
        Attach a text label above each bar displaying its height
        """
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                    '%d' % int(height),
                    ha='center', va='bottom')

    autolabel(rects)
    plt.savefig(file_name + ".png")


def tsne_plot(map_fun_id_performance_counters, file_name):
    raw_data = list(map_fun_id_performance_counters.values())
    data = np.array(raw_data)
    tsne = TSNE(n_components=2, random_state=0)
    tsne_results = tsne.fit_transform(data)
    plt.figure(figsize=(8, 6))
    plt.scatter(tsne_results[:, 0], tsne_results[:, 1], c='blue', marker='o')
    plt.title('t-SNE plot')
    plt.xlabel('t-SNE 1')
    plt.ylabel('t-SNE 2')
    plt.savefig(file_name + ".png")


def tsne_plot_colored(data, index, file_name, plot_title):
    colors = data[:, index]

    # Compute t-SNE embeddings
    tsne = TSNE(n_components=2, random_state=42)
    tsne_results = tsne.fit_transform(data)

    # Create the scatter plot
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(tsne_results[:, 0], tsne_results[:, 1], c=colors, cmap='viridis')
    plt.colorbar(scatter, label='Value of first element')
    plt.title(plot_title) # 't-SNE plot of vectors colored by FP instructions')
    plt.xlabel('t-SNE component 1')
    plt.ylabel('t-SNE component 2')
    plt.savefig(file_name + ".png")


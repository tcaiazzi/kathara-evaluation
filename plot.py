import json
import os
import statistics

import matplotlib.pyplot as plt


def plot_memory_usage(path: str):
    to_plot = {}
    for network_scenario in os.listdir(path):
        values = []
        network_scenario_name = network_scenario.replace("kathara-lab_", "")
        to_plot[network_scenario_name] = {'y': "", 'dy': ""}

        for run_result in os.listdir(os.path.join(path, network_scenario)):
            run_result_path = os.path.join(path, network_scenario, run_result)
            with open(run_result_path, "r") as run_result_file:
                res = json.loads(run_result_file.read())
            values.append(res['mem_usage'])
        to_plot[network_scenario_name]["y"] = statistics.mean(values)
        to_plot[network_scenario_name]["dy"] = (statistics.stdev(values))

    fig, ax = plt.subplots()

    ax.bar(list(to_plot.keys()), list(map(lambda x: x["y"], to_plot.values())), label=list(to_plot.keys()))

    ax.set_ylabel('Memory Usage (MB)')
    ax.set_title('Network Scenarios resource usage')
    ax.legend(title='Network Scenarios')

    plt.savefig(os.path.join(figures_path, "network_scenario_memory.pdf"), format="pdf", bbox_inches='tight')


def plot_startup_time(path: str):
    to_plot = {}
    for network_scenario in os.listdir(path):
        values = []
        network_scenario_name = network_scenario.replace("kathara-lab_", "")
        to_plot[network_scenario_name] = {'y': "", 'dy': ""}

        for run_result in os.listdir(os.path.join(path, network_scenario)):
            run_result_path = os.path.join(path, network_scenario, run_result)
            with open(run_result_path, "r") as run_result_file:
                res = json.loads(run_result_file.read())
            values.append(res['startup_time'])
        to_plot[network_scenario_name]["y"] = statistics.mean(values)
        to_plot[network_scenario_name]["dy"] = (statistics.stdev(values))

    fig, ax = plt.subplots()

    ax.bar(list(to_plot.keys()), list(map(lambda x: x["y"], to_plot.values())), label=list(to_plot.keys()))

    ax.set_ylabel('Startup Time (sec)')
    ax.set_title('Network Scenarios Startup Time')
    ax.legend(title='Network Scenarios')

    plt.savefig(os.path.join(figures_path, "network_scenario_startup_time.pdf"), format="pdf", bbox_inches='tight')


if __name__ == '__main__':
    figures_path = "figures"
    os.makedirs(figures_path, exist_ok=True)

    results_path = "results"

    plot_memory_usage(results_path)
    plot_startup_time(results_path)

import json
import os
import statistics
import numpy as np

import matplotlib.pyplot as plt


def extract_bars_values(path: str, field_name: str):
    results = {}
    for network_scenario in os.listdir(path):
        network_scenario_path = os.path.join(path, network_scenario)
        network_scenario_name = network_scenario.replace("kathara-lab_", "")
        values = []
        for platform in os.listdir(network_scenario_path):
            platform_result_path = os.path.join(network_scenario_path, platform)
            if not platform in results:
                results[platform] = {}
            for run_result in os.listdir(platform_result_path):
                run_result_path = os.path.join(platform_result_path, run_result)
                with open(run_result_path, "r") as run_result_file:
                    res = json.loads(run_result_file.read())
                values.append(res[field_name])

            results[platform][network_scenario_name] = {}
            results[platform][network_scenario_name]["y"] = statistics.mean(values)
            results[platform][network_scenario_name]["dy"] = (statistics.stdev(values))
    return results


def plot_bars(parsed_results, colors, ax):
    x = np.arange(len(parsed_results["linux"].keys()))  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0

    for idx, (platform, platform_result) in enumerate(parsed_results.items()):
        values_to_plot = list(map(lambda result: result["y"], platform_result.values()))
        errors_to_plot = list(map(lambda result: result["dy"], platform_result.values()))
        offset = width * multiplier
        rects = ax.bar(x + offset, values_to_plot, width, yerr=errors_to_plot,  label=platform, color=colors[platform],
                       alpha=0.8, edgecolor='black', linewidth=1)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.set_xticks(x + width, parsed_results["linux"].keys())

def plot_memory_usage(path: str):
    parsed_results = extract_bars_values(path, "mem_usage")

    fig, ax = plt.subplots(layout='constrained')
    colors = {
        "linux": "orange",
        "windows": "blue",
        "osx": "green"
    }

    plot_bars(parsed_results, colors, ax)

    ax.set_ylabel('Memory Usage (MB)')
    ax.set_title('Network Scenarios resource usage')
    ax.legend(title='Network Scenarios')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.savefig(os.path.join(figures_path, "network_scenario_memory.pdf"), format="pdf", bbox_inches='tight')


def plot_startup_time(path: str):
    parsed_results = extract_bars_values(path, "startup_time")

    fig, ax = plt.subplots(layout='constrained')
    colors = {
        "linux": "orange",
        "windows": "blue",
        "osx": "green"
    }

    plot_bars(parsed_results, colors, ax)

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

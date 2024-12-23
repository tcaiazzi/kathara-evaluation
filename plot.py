import json
import os
import statistics
import numpy as np

import matplotlib.pyplot as plt

platform_to_label = {
    "win32": "Windows",
    "linux": "Linux",
    "darwin": "macOS"
}

# platform_to_color = {
#     "linux": "orange",
#     "win32": "blue",
#     "darwin": "green"
# }

platform_to_color = {
    "linux": "sandybrown",
    "win32": "lightblue",
    "darwin": "lightgreen"
}

platform_to_error_color = {
    "linux": "brown",
    "win32": "blue",
    "darwin": "green"
}




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
            results[platform][network_scenario_name]["min_y"] = (min(values))
            results[platform][network_scenario_name]["max_y"] = (max(values))

    return results


def plot_bars(parsed_results, ax):
    x = np.arange(len(parsed_results["linux"].keys()))  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0

    for idx, (platform, platform_result) in enumerate(parsed_results.items()):
        values_to_plot = list(map(lambda result: result["y"], platform_result.values()))
        errors_to_plot = list(map(lambda result: (result['min_y'], result['max_y']), platform_result.values()))
        offset = width * multiplier
        rects = ax.bar(x + offset, values_to_plot, width, label=platform_to_label[platform],
                       color=platform_to_color[platform], edgecolor='black', linewidth=1,
                       align='center', ecolor='black', capsize=10,
                       )

        for i, y in enumerate(values_to_plot):
            plt.errorbar(
                x[i] + offset, y,
                yerr=[[y - errors_to_plot[i][0]],
                      [errors_to_plot[i][1] - y]],
                color=platform_to_error_color[platform], elinewidth=1.5, capsize=1.5
            )

        # ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.set_xticks(x + width, parsed_results["linux"].keys())


def plot_memory_usage(path: str):
    parsed_results = extract_bars_values(path, "mem_usage")

    fig, ax = plt.subplots(layout='constrained')
    ax.set_axisbelow(True)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    ax.tick_params(axis='both', labelsize=15)

    plot_bars(parsed_results, ax)

    ax.set_ylabel('Memory Usage (MB)', fontsize=15)
    ax.legend(fontsize=15)

    plt.savefig(os.path.join(figures_path, "network_scenario_memory.pdf"), format="pdf", bbox_inches='tight')


def plot_startup_time(path: str):
    parsed_results = extract_bars_values(path, "startup_time")

    fig, ax = plt.subplots(layout='constrained')
    ax.set_axisbelow(True)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    ax.tick_params(axis='both', labelsize=15)
    plot_bars(parsed_results, ax)

    ax.set_ylabel('Startup Time (sec)', fontsize=15)
    ax.legend(fontsize=15)

    plt.savefig(os.path.join(figures_path, "network_scenario_startup_time.pdf"), format="pdf", bbox_inches='tight')


if __name__ == '__main__':
    figures_path = "figures"
    os.makedirs(figures_path, exist_ok=True)

    results_path = "results"

    plot_memory_usage(results_path)
    plot_startup_time(results_path)

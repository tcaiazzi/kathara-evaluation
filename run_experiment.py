import argparse
import json
import os
import sys
import time
from datetime import timedelta

from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab
from Kathara.parser.netkit.LabParser import LabParser
from Kathara.setting.Setting import Setting
from Kathara.manager.docker.stats.DockerMachineStats import DockerMachineStats


def extract_mem_usage_and_convert(mem_usage: str):
    split_line = mem_usage.split("/")[0].split(" ")
    value = float(split_line[0])
    unit = split_line[1]

    if "KB" in unit:
        value = value / 1000
    if "GB" in unit:
        value = value * 1000

    return value


def extract_cpu_usage(cpu_usage: str):
    return float(cpu_usage.split("%")[0])


def deploy_network_scenario(network_scenario: Lab):
    Kathara.get_instance().deploy_lab(network_scenario)


def get_network_scenario_memory_usage(network_scenario: Lab):
    stats = next(Kathara.get_instance().get_machines_stats(lab=network_scenario))
    result = {
        'mem_usage': 0,
        'cpu_usage': 0
    }

    for device_name, stat in stats.items():
        stat: DockerMachineStats
        result["mem_usage"] += extract_mem_usage_and_convert(stat.mem_usage)
        result["cpu_usage"] += extract_cpu_usage(stat.cpu_usage)

    return result

def run_experiment(network_scenario_path: str, run_number: int):
    Kathara.get_instance().wipe()

    start_time = time.monotonic()

    network_scenario = LabParser.parse(network_scenario_path)

    deploy_network_scenario(network_scenario)

    end_time = time.monotonic()
    total_time = timedelta(seconds=end_time - start_time).total_seconds()

    print(f"Network scenario startup time: {total_time} seconds")

    res = get_network_scenario_memory_usage(network_scenario)
    res["startup_time"] = total_time

    print(f"Network scenario memory usage: {res['mem_usage']} MB")

    results_directory = os.path.join("results", os.path.split(os.path.abspath(network_scenario_path))[-1])
    os.makedirs(results_directory, exist_ok=True)
    result_path = os.path.join(results_directory, f"run_{run_number}.json")
    with open(result_path, "w") as results_file:
        results_file.write(json.dumps(res))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A tool to get Kathará network scenarios resource usage.',
        add_help=True
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--network-scenario",
        help='The path to the network scenario on which run the experiments.',
    )

    group.add_argument(
        "--all-scenarios",
        help='The path to the base network scenarios directory.',
    )

    parser.add_argument(
        "--runs",
        help='The number of time to execute the experiment.',
        type=int,
        required=False
    )

    Setting.get_instance().load_from_dict({"network_plugin": "kathara/katharanp"})

    args = parser.parse_args(sys.argv[1:2])

    runs = args.runs if args.runs else 3

    if args.network_scenario:
        print(f"Running experiments on: {args.network_scenario}...")
        for run  in range(runs):
            print(f"Starting run {run}...")
            run_experiment(args.network_scenario, run)
    elif args.all_scenarios:
        print(f"Running experiments on network scenarios in: {args.all_scenarios}...")
        for scenario in os.listdir(args.all_scenarios):
            scenario_path = os.path.join(args.all_scenarios, scenario)
            print(f"Running experiments on: {scenario_path}...")
            for run in range(runs):
                print(f"Starting run {run}...")
                run_experiment(scenario_path, run)

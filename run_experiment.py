import argparse
import json
import os
import subprocess
import sys
import time
from datetime import timedelta

from Kathara.manager.Kathara import Kathara
from Kathara.manager.docker.stats.DockerMachineStats import DockerMachineStats
from Kathara.model.Lab import Lab
from Kathara.model.Machine import Machine
from Kathara.parser.netkit.LabParser import LabParser
from Kathara.setting.Setting import Setting


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
        print(f"{stat.name}: {stat.mem_usage}")

    return result


def open_terminal(device: Machine) -> None:
    command = (
        '%s -c "from Kathara.manager.Kathara import Kathara; '
        "Kathara.get_instance().connect_tty('%s', lab_hash='%s', shell='%s', logs=True)\""

    )
    command = "{python -m kathara connect -d %s %s}" % (device.lab.fs_path(), device.name)
    if sys.platform == 'win32':
        subprocess.Popen(["powershell", "start-process", "powershell", command], start_new_session=True)
    else:
        subprocess.Popen([Setting.get_instance().terminal, "-e", command], start_new_session=True)


def run_experiment(network_scenario_path: str, run_number: int):
    print(Setting.get_instance().terminal)

    network_scenario_path = os.path.abspath(network_scenario_path)

    Kathara.get_instance().wipe()

    start_time = time.monotonic()

    network_scenario = LabParser.parse(network_scenario_path)

    Kathara.get_instance().deploy_lab(lab=network_scenario)

    for machine in network_scenario.machines.values():
        open_terminal(machine)

    end_time = time.monotonic()
    total_time = timedelta(seconds=end_time - start_time).total_seconds()

    print(f"Network scenario startup time: {total_time} seconds")

    res = get_network_scenario_memory_usage(network_scenario)
    res["startup_time"] = total_time

    print(f"Network scenario memory usage: {res['mem_usage']} MB")

    Kathara.get_instance().undeploy_lab(lab=network_scenario)

    results_directory = os.path.join("results", os.path.split(os.path.abspath(network_scenario_path))[-1], sys.platform)
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

    args = parser.parse_args(sys.argv[1:])

    runs = args.runs if args.runs else 3

    if args.network_scenario:
        print(f"Running experiments on: `{args.network_scenario}`")
        for run in range(runs):
            print(f"Starting run {run}...")
            run_experiment(args.network_scenario, run)
    elif args.all_scenarios:
        print(f"Running experiments on network scenarios in: `{args.all_scenarios}`")
        for scenario in os.listdir(args.all_scenarios):
            scenario_path = os.path.join(args.all_scenarios, scenario)
            print(f"Running experiments on: {scenario_path}...")
            for run in range(runs):
                print(f"Starting run {run}...")
                run_experiment(scenario_path, run)

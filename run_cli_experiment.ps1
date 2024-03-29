$scenarios_path = "network-scenarios"
$result_path = "results/cli"
$log_file = "log.txt"
$os_name = [System.Environment]::OSVersion.Platform.ToString()

Remove-Item -Path "$result_path\$os_name" -Recurse -Force
New-Item -ItemType Directory -Path "$result_path\$os_name" | Out-Null
New-Item -ItemType Directory -Path "$result_path\$os_name\time" | Out-Null
New-Item -ItemType Directory -Path "$result_path\$os_name\mem" | Out-Null

kathara wipe -f

foreach ($dir in Get-ChildItem -Path "$scenarios_path" -Directory) {
    $lab = $dir.Name
    $labPath = "$scenarios_path\$lab"
    echo $labPath
    echo $lab

    for ($i = 0; $i -le 10; $i++) {
        # Extract the directory name
        echo $i
        echo "kathara lstart -d $labPath"

        Measure-Command { kathara lstart -d $labPath } | Select-Object -ExpandProperty TotalSeconds | Out-File -FilePath "$result_path\$os_name\time\$lab-log.txt" -Append
        kathara linfo -d $dir | Select-String -Pattern '[0-9.]+\sMB' | ForEach-Object { $_.Matches.Value.Split(' ')[0] } | Out-File -FilePath "$result_path\$os_name\mem\lab-log-$i.txt"
        kathara lclean -d $dir.FullName | Out-Null
    }

}

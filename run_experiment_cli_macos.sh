#!\bin\bash
TIMEFORMAT=%R

scenarios_path="network-scenarios"
result_path="results/cli"
log_file="log.txt"
os_name=$(uname -s)

rm -r $result_path/$os_name
mkdir -p $result_path/$os_name
mkdir -p $result_path/$os_name/time
mkdir -p $result_path/$os_name/mem

kathara wipe -f

for dir in "$scenarios_path"/*/; do
    # Extract the directory name
    lab=$(basename "$dir")
    echo $lab
    echo $dir
    for ((i = 0; i <= 10; i++)); do
        echo $i
        start_time=$(date +%s)
        kathara lstart -d $dir
        end_time=$(date +%s)
        execution_time=$(((end_time-start_time)))
        seconds=$(( execution_time ))
        echo $seconds 
        printf "%d\n" $seconds >> "$result_path/$os_name/time/$lab-time.txt"
        kathara linfo -d $dir | grep -o '[0-9.]\+ MB' | cut -d ' ' -f 1 > "$result_path/$os_name/mem/$lab-log-$i.txt"
        kathara lclean -d $dir >/dev/null 2>&1
    done
done

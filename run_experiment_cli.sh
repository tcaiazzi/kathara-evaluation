#!\bin\bash
TIMEFORMAT=%R

scenarios_path="network-scenarios"
result_path="results/cli"
log_file="log.txt"
os_name=$(uname -s)

rm -r $result_path/$os_name
mkdir -p $result_path/$os_name

kathara wipe -f

for dir in "$scenarios_path"/*/; do
    # Extract the directory name
    lab=$(basename "$dir")
    echo $lab
    echo $dir
    for ((i = 0; i <= 10; i++)); do
        echo $i
        { time kathara lstart -d $dir 2>&1 | grep real ; }  2>> "$result_path/$os_name/$lab-log.txt"
        kathara lclean -d $dir >/dev/null 2>&1
    done
done

# find "$scenarios_path" -mindepth 1 -maxdepth 1 -type d -execdir \
#   bash -c '; ;
#   ; kathara lclean -d $dir' \;

# time kathara lstart -d network-scenarios/kathara-lab_small-internet
#
# kathara lclean -d network-scenarios/kathara-lab_small-internet{ time sleep 1; } 2>&1 | grep real

#!/bin/sh
# Run 4 clingo processes in parallel, each pinned to a specific CPU core, writing output to out-<n>.txt files.

if [ $# -lt 1 ]; then
    echo "Usage: $0 <facts-file> [time-limit]" >&2
    exit 1
fi

for f in concretize.lp heuristic.lp direct_dependency.lp libc_compatibility.lp; do
    if [ ! -f "$f" ]; then
        echo "Error: Required file '$f' not found." >&2
        exit 1
    fi
done

facts_file="$1"
time_limit="${2:-50}"

trap 'pkill -P $$; exit 130' INT

for i in $(seq 0 3); do
    (
        for j in $(seq $i 4 50); do
            echo "Run $j (CPU $i)"
            shuffled_file="shuffled.$j.lp"
            ./shuffle.py < "$facts_file" > "$shuffled_file"
            taskset -c $i clingo --time-limit="$time_limit" --verbose=3 --stats=2 --configuration=tweety --opt-strategy=usc,one,1 --heuristic=Domain concretize.lp heuristic.lp direct_dependency.lp libc_compatibility.lp "$shuffled_file" > out-$j.txt
        done
    ) &
done
wait

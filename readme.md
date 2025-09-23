Run the clingo solver with shuffled output in parallel using this:

```
$ ./run_clingo.sh <file.lp> [time_limit]
```

Then parse the output and show diffs between subsequent answers using this:

```
$ python3 parse_clingo_output.py < clingo-output.txt
```

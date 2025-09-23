Run the clingo solver with shuffled output in parallel using this:

```
$ ./run-clingo.sh <file.lp> [time_limit]
```

Then parse the output and show diffs between subsequent answers using this:

```
$ ./diff-solutions.py < out-0.txt
```

or any other `out-*.txt` file

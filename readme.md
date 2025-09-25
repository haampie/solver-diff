This repo is meant to help analyze Spack's solver performance:

1. What is the solver stuck on when it fails to find a solution in reasonable time?
2. If optimal solutions are not distinct, what's the difference?

## Getting started

Install `clingo-bootstrap@5.8:` and make it available in your PATH:

```
spack install clingo-bootstrap@5.8:
```

Then copy or symlink the following files into this directory:

```
spack=/path/to/spack
for f in concretize.lp heuristic.lp direct_dependency.lp libc_compatibility.lp; do
    ln -s $spack/lib/spack/spack/solver/$f $f
done
```

Generate an input file for clingo from Spack using:

```
spack solver --show=asp <your spec> > problem.lp
```

Now run multiple parallel solves of the same, shuffled problem with:

```
$ ./run-clingo.sh problem.lp [time_limit]
```

## Analyzing results

Then you can do two things:

1. Show the diff between intermediate solutions from a single solver run

   ```
   $ ./diff-solutions.py out-0.json
   ```

   This can help identify what the solver needs to change to get "unstuck". As an example, it can
   help identify that certain properties have to be changed all at once to improve the optimization
   score, while tweaking individual properties does not contribute to improving the score. That
   can indicate that better optimization criteria may be needed to make progress incrementally.

2. Compare the final solutions of two different solver runs:

   ```
   $ ./diff-solutions.py out-0.json out-1.json
   ```

   Typically Spack's solutions are deterministic at the level of the output spec, but in practice
   there are often multiple distinct optimal solutions that map to the same concrete spec. If there
   are loads of unique solutions, the solver may spend time proving optimality even though it has
   already determined the optimal solution.

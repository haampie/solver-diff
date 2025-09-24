This repo is meant to help analyze Spack's solver performance:

1. What is the solver stuck on when it fails to find a solution in reasonable time?
2. If optimal solutions are not distinct, what's the difference?

## Getting started

To get started, copy or symlink the following files into this directory:

```
spack=/path/to/spack
ln -s $spack/lib/spack/spack/solver/concretize.lp concretize.lp
ln -s $spack/lib/spack/spack/solver/heuristic.lp heuristic.lp
ln -s $spack/lib/spack/spack/solver/direct_dependency.lp direct_dependency.lp
ln -s $spack/lib/spack/spack/solver/libc_compatibility.lp libc_compatibility.lp
```

Then, generate an input file for clingo from Spack using:

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
   $ ./diff-solutions.py out-0.txt
   ```

   This can help identify what the solver needs to change to get "unstuck". As an example, it can
   help identify that certain properties have to be changed all at once to improve the optimization
   score, while tweaking individual properties does not contribute to improving the score. That
   can indicate that better optimization criteria so progress can be made "greedily".

2. Compare the final solutions of two different solver runs:

   ```
   $ ./diff-solutions.py out-0.txt out-1.txt
   ```

   Typically Spack's solutions are deterministic at the level of the output spec, but in practice
   there are often multiple distinct optimal solutions that map to the same concrete spec. If there
   are loads of unique solutions, the solver may spend time proving optimality even though it has
   already determined the optimal solution.

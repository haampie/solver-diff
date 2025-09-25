#!/usr/bin/env python3
import argparse, sys
import json

def get_solutions(data: dict):
    return [w for w in data["Call"][-1]["Witnesses"] if "Value" in w]

def sort_facts(witness) -> list[str]:
    facts = witness["Value"]
    facts.sort()
    return facts


def get_last_answer(data: dict) -> list[str]:
    """Extract facts from the last answer in clingo output."""
    *_, last = (w for w in data["Call"][-1]["Witnesses"] if "Value" in w)
    return sort_facts(last)


def print_diff(
    prev: list[str], curr: list[str], file_before: str, file_after: str
) -> None:
    sys.stdout.write(f"\033[1m--- {file_before}\n+++ {file_after}\033[0m\n")
    i = j = 0
    while i < len(prev) and j < len(curr):
        if prev[i] == curr[j]:
            i, j = i + 1, j + 1
        elif prev[i] < curr[j]:
            sys.stdout.write(f"\033[91m-{prev[i]}\033[0m\n")
            i += 1
        else:
            sys.stdout.write(f"\033[92m+{curr[j]}\033[0m\n")
            j += 1
    while i < len(prev):
        sys.stdout.write(f"\033[91m-{prev[i]}\033[0m\n")
        i += 1
    while j < len(curr):
        sys.stdout.write(f"\033[92m+{curr[j]}\033[0m\n")
        j += 1


def intermediate_diffs(data: dict) -> None:
    """Extract answers from clingo output and print diffs between them."""
    curr_witness = None
    prev_witness = None
    solutions = get_solutions(data)

    for i, witness in enumerate(solutions):
        sort_facts(witness)
        prev_witness, curr_witness = curr_witness, witness
        if i > 1:
            print_diff(
                prev_witness["Value"],
                curr_witness["Value"],
                file_before=f"answer {i}",
                file_after=f"answer {i + 1}",
            )
            num_digits = [max(len(str(x)), len(str(y))) for x, y in zip(prev_witness["Costs"], curr_witness["Costs"])]
            prev_str = ",".join(f"{d:>{n}}" for d, n in zip(prev_witness["Costs"], num_digits))
            curr_str = ",".join(f"{c:>{n}}" for c, n in zip(curr_witness["Costs"], num_digits))
            sys.stdout.write(
                f"\n\033[91m-opt: {prev_str}\033[0m\n\033[92m+opt: {curr_str}\033[0m\n\n"
            )

    all_times = [data["Call"][-1]["Start"], *(w["Time"] for w in solutions), data["Call"][-1]["Stop"]]

    print(f"   Start: {all_times[0]:5.1f}s")
    for i in range(1, len(all_times)):
         time_delta = all_times[i] - all_times[i - 1]
         preamble = f"{i:>2} to {i+1:>2}:" if i < len(all_times) - 1 else "    Stop:"
         print(f"{preamble} {all_times[i]:5.1f}s [{time_delta:5.1f}s]")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Parse and diff clingo output")
    p.add_argument("file1", help="First clingo output file")
    p.add_argument("file2", nargs="?", help="Second clingo output file (optional)")

    args = p.parse_args()

    with open(args.file1) as input_file:
        data1 = json.load(input_file)

    if args.file2:
        with open(args.file2) as f2:
            data2 = json.load(f2)
        facts1 = get_last_answer(data1)
        facts2 = get_last_answer(data2)
        print_diff(facts1, facts2, file_before=args.file1, file_after=args.file2)
    else:
        intermediate_diffs(data1)

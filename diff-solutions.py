#!/usr/bin/env python3
import argparse, re, sys
from typing import TextIO

STRING = re.compile(r'"[^"]*"')


def get_facts(line: str) -> list[str]:
    facts = STRING.sub(lambda m: m.group(0).replace(" ", "_"), line.strip()).split()
    facts.sort()
    return facts


def filename(i: int) -> str:
    return f"answer-{i}.txt"


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


def get_last_answer(input_file: TextIO) -> list[str]:
    """Extract facts from the last answer in clingo output."""
    lines = input_file.read().splitlines()
    last_answer_line = None

    for i, line in enumerate(lines):
        if line.startswith("Answer:"):
            last_answer_line = lines[i + 1]

    return get_facts(last_answer_line) if last_answer_line else []


def intermediate_diffs(input_file: TextIO) -> None:
    """Extract answers from clingo output and print diffs between them."""
    is_answer = False
    curr, prev, answer_id = [], [], 0
    curr_opt, prev_opt = "", ""
    for line in input_file:
        if is_answer:
            prev, curr = curr, get_facts(line)
            with open(filename(answer_id), "w") as f:
                f.write("\n".join(curr))
            if answer_id > 1:
                print_diff(
                    prev,
                    curr,
                    file_before=filename(answer_id - 1),
                    file_after=filename(answer_id),
                )
            is_answer = False
        elif line.startswith("Answer:"):
            is_answer, answer_id = True, answer_id + 1
        elif line.startswith("Optimization:"):
            prev_opt, curr_opt = curr_opt, line[13:].strip()
            if answer_id > 1:
                sys.stdout.write(
                    f"\033[91m-opt: {prev_opt}\033[0m\n\033[92m+opt: {curr_opt}\033[0m\n\n"
                )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Parse and diff clingo output")
    p.add_argument("file1", help="First clingo output file")
    p.add_argument("file2", nargs="?", help="Second clingo output file (optional)")

    args = p.parse_args()

    if args.file2:
        with open(args.file1) as f1, open(args.file2) as f2:
            facts1 = get_last_answer(f1)
            facts2 = get_last_answer(f2)
        print_diff(facts1, facts2, file_before=args.file1, file_after=args.file2)
    else:
        with open(args.file1) as input_file:
            intermediate_diffs(input_file)

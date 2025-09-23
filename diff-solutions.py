#!/usr/bin/env python3
import argparse, re, sys
from typing import TextIO

TOKENIZER = re.compile(r'("[^"]*")|(\)(?: |$))|(\)|[^")]+)')


def get_facts(line: str) -> list[str]:
    facts = TOKENIZER.sub(
        lambda m: ")\n" if m.group(2) else m.group(0), line.strip()
    ).split("\n")
    facts.sort()
    return facts

def filename(i: int) -> str:
    return f"answer-{i}.txt"

def parse_clingo_output(input_file: TextIO) -> None:
    is_answer = False
    curr, prev, answer_id = [], [], 0
    curr_opt, prev_opt = "", ""
    for line in input_file:
        if is_answer:
            prev, curr = curr, get_facts(line)
            with open(filename(answer_id), "w") as f:
                f.write("\n".join(curr))
            if answer_id > 1:
                sys.stdout.write(
                    f"\033[1m--- {filename(answer_id - 1)}\n+++ {filename(answer_id)}\033[0m\n"
                )
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
            is_answer = False
        elif line.startswith("Answer:"):
            is_answer, answer_id = True, answer_id + 1
        elif line.startswith("Optimization:"):
            prev_opt, curr_opt = curr_opt, line[13:].strip()
            if answer_id > 1:
                sys.stdout.write(f"\033[91m-opt: {prev_opt}\033[0m\n\033[92m+opt: {curr_opt}\033[0m\n\n")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Parse and diff clingo output")
    p.add_argument("-i", help="Input file (default: stdin)")
    args = p.parse_args()

    input = open(args.i, "r") if args.i else sys.stdin
    parse_clingo_output(input)

#!/usr/bin/env python3
import random
import re
import sys
statements = re.split(r'(?<=\.\n)', sys.stdin.read())
random.shuffle(statements)
sys.stdout.write("".join(statements))

#!/usr/bin/env python3

import sys
import re

# Find the value inside href="..."
url_pattern = re.compile(r'href="([^"]*)"')

for line in sys.stdin:
    matches = url_pattern.findall(line)

    for url in matches:
        print(f"{url}\t1")

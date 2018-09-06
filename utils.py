#! /usr/bin/python

import re

# Just the first line that starts with <starting_match>
def get_first_matching_line(f, starting_match):
    for line in f:
        if starting_match == line[:len(starting_match)]:
            return line.rstrip()
    f.seek(0)
    raise ValueException('No matching line found!')

# All lines that start with <starting_match>
def get_all_lines_start_matching(f, starting_match):
    lines = []
    for line in f:
        if starting_match == line[:len(starting_match)]:
            lines.append(line.rstrip())
    f.seek(0)
    return lines

# Will return just the line, not the matching groups
def search_all_lines_with_regex(f, regex):
    lines = []

    for line in f:
        match = re.search(regex, line)
        if match:
            lines.append(line)
    f.seek(0)
    return lines

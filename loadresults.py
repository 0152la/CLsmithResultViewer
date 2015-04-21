#!/usr/bin/python

import os
import glob
import collections
import re

def ParseData(location = os.getcwd()):
    os.chdir(location)
    files = glob.glob("*.csv")
    numeric_value = re.compile(r'[^0-9a-fx]')
    votes_min = 3

    raw_contents = dict()
    contents = dict()
    line_nos = dict()

    " Read raw contents from csv files"
    print("Reading results from files...")
    for filename in files:
        platform_name = ' '.join(filename.split('.')[0].split('_'))
        csvfile = open(filename, 'r')
        raw_contents[platform_name] = csvfile.read().splitlines()
        raw_contents[platform_name] = [s.strip() for s in \
                                    (filter(None, raw_contents[platform_name]))]

    " Organize raw contents "
    print("Organizing raw results...")
    for platform in raw_contents:
        for line in raw_contents[platform]:
            " Expected line format: RESULTS FOR <prog_name>.cl (<no_lines>) "
            if "RESULTS FOR" in line:
                program = line.split(" ")[2]
                if program not in contents:
                    contents[program] = dict()
                contents[program][platform] = []
                if program not in line_nos:
                    if "(" not in line:
                        continue
                    line_nos[program] = line.split("(")[1].split(")")[0]
            else:
                contents[program][platform].append(line)
    raw_contents.clear()

    " Parse numeric values to uniformly have 0x in the beginning "
    print("Making data uniform...")
    for program in contents:
        for platform in contents[program]:
            contents[program][platform] = "\n".join(sorted(contents[program][platform]))
            if bool(numeric_value.match(contents[program][platform])):
                continue
            parsed_value = []
            for result in contents[program][platform].split(","):
                result = result.strip()
                if not result:
                    continue
                if not result.startswith("0x"):
                    parsed_value.append("0x" + result)
                else:
                    parsed_value.append(result)
            contents[program][platform] = ",".join(sorted(parsed_value))

    " Find majority vote for each program "
    print("Computing majorities...")
    vote = dict()
    sample = dict()
    for program in contents:
        vote[program] = dict()
        for platform in contents[program]:
            curr_result = contents[program][platform]
            if not curr_result.startswith("0x"):
                continue
            if curr_result in vote[program]:
                vote[program][curr_result] += 1
            else:
                vote[program][curr_result] = 0
        curr_max = 0
        curr_cand = []
        for candidate, votes in vote[program].items():
            if votes > curr_max:
                curr_max = votes
                curr_cand = [candidate]
            elif votes == curr_max:
                curr_cand.append(candidate)
        if len(curr_cand) != 1 or curr_max < votes_min:
            sample[program] = "Inconclusive"
        else:
            sample[program] = curr_cand[0]
    vote.clear

    return sample, contents, line_nos

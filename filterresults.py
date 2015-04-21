import re

numeric_value = re.compile(r'[^0-9a-fx]')

def FilterMatching(sample, contents, target, filter_fails = False):
  filtered_progs = []
  for program in sample:
    if sample[program] != contents[program][target]:
      if filter_fails and bool(numeric_value.match(contents[program][target])):
        continue
      filtered_progs.append(program)
  return sorted(filtered_progs)

def FilterPlat(contents, target, filter_plat, filter_fails = False):
  filtered_progs = []
  for program in contents:
    if contents[program][target] != contents[program][filter_plat]:
      if filter_fails and bool(numeric_value.match(contents[program][target])):
        continue
      filtered_progs.append(program)
  return sorted(filtered_progs)

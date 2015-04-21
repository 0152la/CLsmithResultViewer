def FilterMatching(sample, contents, target):
  filtered_progs = []
  for program in sample:
    if sample[program] != contents[program][target]:
      filtered_progs.append(program)
  return sorted(filtered_progs)

def FilterPlat(contents, target, filter_plat):
  filtered_progs = []
  for program in contents:
    if contents[program][target] != contents[program][filter_plat]:
      filtered_progs.append(program)
  return sorted(filtered_progs)

def OutputHTML(prog_list, sample, contents):
  print("hi")

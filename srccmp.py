import sys
import os
from src import src, to_json
from cmp import cmp

help = f"""\
Compare two or more sorce projects.
  Use:
    {(os.path.split(sys.argv[0])[1])} <setting.cfg> <path__1> <path__2> [<path_3> [ ...]]
"""

if __name__ == "__main__":
  if len(sys.argv) < 4:
    print(help)
    exit(1)
  cfg = sys.argv[1]
  if not os.path.isfile(cfg):
    print(f"Not found file \"{cfg}\"!")
    exit(1)
  pjs = sys.argv[2:]
  for pj in  pjs:
    if not os.path.isdir(pj):
      print(f"Not found directory \"{pj}\"!")
      exit(1)
  # srcs = [{"source_location_root":pj} for pj,i in zip(pjs,range(len(pjs)))]
  srcs = [src(cfg, pj, "%s.src" % (i+1)) for pj,i in zip(pjs,range(len(pjs)))]
  for i in range(len(srcs)):
    for j in range(i+1,len(srcs)):
      out_name = "%s-%s.cmp" % (i+1,j+1)
      print( out_name )
      to_json(cmp(srcs[i], srcs[j]), out_name)

      # print(srcs[i]["source_location_root"])



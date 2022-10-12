import os
import re
import sys
import json
import config_json
import functools
import difflib

def diff_lines(AA:list,BB:list)->dict:
  ret = {" ": 0, "-": 0, "+": 0, "?": 0}
  for i in difflib.Differ().compare(AA, BB):
    ret[i[0]]+=1
  return ret

def os_only_name(filename):
  return os.path.splitext(os.path.split(filename)[1])[0]

def to_json(obj,filename = ".json"):
  with open(filename,"w", encoding = "utf-8") as f:
    json.dump(obj, f, indent = 1, ensure_ascii = False)

def from_json(filename = ".json"):
  with open(filename,"r", encoding = "utf-8") as f:
    return json.load(f)

def dbg(name, context = vars()):
  return
  obj = context[name] if name in context else {}
  to_json(obj,name+".dbg")

def percent_of(a:int,b:int)->int:
  return round(a/b*100)

def cmp(A_src:dict, B_src:dict)->dict:
  res = {}
  res["Расположение проекта A"] = A_src["source_location_root"]
  res["Расположение проекта B"] = B_src["source_location_root"]

  ### Статистика по файлам

  A_keys = list(A_src["files"].keys()) ; res["Файлов всего в проекте A"] = len(A_keys) ; dbg("A_keys")
  B_keys = list(B_src["files"].keys()) ; res["Файлов всего в проекте B"] = len(B_keys) ; dbg("B_keys")

  A_only = sorted([i for i in A_keys if i not in B_keys]) ; res["Файлов уникальных в проекте A"] = len(A_only) ; dbg("A_only")
  B_only = sorted([i for i in B_keys if i not in A_keys]) ; res["Файлов уникальных в проекте B"] = len(B_only) ; dbg("B_only")

  AB_keys = sorted([i for i in A_keys if i in B_keys]) ; res["Файлов общих всего"] = len(AB_keys) ; dbg("AB_keys")

  AB_ne = [i for i in AB_keys if A_src["files"][i]["hash"] != B_src["files"][i]["hash"] ] ; res["Файлов общих изменённых"] = len(AB_ne) ; dbg("AB_ne")
  AB_eq = [i for i in AB_keys if A_src["files"][i]["hash"] == B_src["files"][i]["hash"] ] ; res["Файлов общих одинаковых"] = len(AB_eq) ; dbg("AB_eq")

  res["Файлов удаленных (% от A)"] = percent_of(res["Файлов уникальных в проекте A"],res["Файлов всего в проекте A"])
  res["Файлов добавленных (% от B)"] = percent_of(res["Файлов уникальных в проекте B"],res["Файлов всего в проекте B"])
  res["Файлов изменённых (% от B)"] = percent_of(res["Файлов общих изменённых"],res["Файлов всего в проекте B"])
  res["Файлов одинаковых (% от B)"] = percent_of(res["Файлов общих одинаковых"],res["Файлов всего в проекте B"])

  ### Статистика по строкам

  res["Строк всего в A"] = functools.reduce(lambda a,i: a+len(A_src["files"][i]["lines"]), A_keys, 0)
  res["Строк всего в B"] = functools.reduce(lambda a,i: a+len(B_src["files"][i]["lines"]), B_keys, 0)
  A_lines_del = functools.reduce(lambda a,i: a+len(A_src["files"][i]["lines"]), A_only, 0)
  B_lines_add = functools.reduce(lambda a,i: a+len(B_src["files"][i]["lines"]), B_only, 0)

  AB_lines_eq = functools.reduce(lambda a,i: a+len(A_src["files"][i]["lines"]), AB_eq, 0)
  AB_lines_ne_by_files = {i: diff_lines(A_src["files"][i]["lines"],B_src["files"][i]["lines"]) for i in AB_ne}
  AB_lines_ne_del = functools.reduce(lambda a,i: a+AB_lines_ne_by_files[i]["-"],AB_lines_ne_by_files,0)
  AB_lines_ne_equ = functools.reduce(lambda a,i: a+AB_lines_ne_by_files[i][" "],AB_lines_ne_by_files,0)
  AB_lines_ne_add = functools.reduce(lambda a,i: a+AB_lines_ne_by_files[i]["+"],AB_lines_ne_by_files,0)

  res["Строк удаленных"] = A_lines_del+AB_lines_ne_del
  res["Строк добавленных"] = B_lines_add+AB_lines_ne_add
  res["Строк одинаковых"] = AB_lines_eq+AB_lines_ne_equ

  res["Строк удаленных (% от A)"] = percent_of(res["Строк удаленных"],res["Строк всего в A"])
  res["Строк добавленных (% от B)"] = percent_of(res["Строк добавленных"],res["Строк всего в B"])
  res["Строк одинаковых (% от B)"] = percent_of(res["Строк одинаковых"],res["Строк всего в B"])

  return res


if __name__ == "__main__":
  res_file = "AB.cmp"
  A_file = "A.src"
  B_file = "B.src"

  if len(sys.argv) > 1:
    A_file = sys.argv[1]
  if len(sys.argv) > 2:
    B_file = sys.argv[2]
  if len(sys.argv) > 3:
    res_file = sys.argv[3]

  to_json(cmp(from_json(A_file), from_json(B_file)),res_file)
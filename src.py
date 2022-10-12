import os
import re
import sys
import json
import config_json
import functools as ft
import hashlib

def hash(s:str):
  return hashlib.md5(s.encode()).hexdigest()

def walk_by_root(root="."):
  re_root = re.compile(re.escape(root+os.sep))
  result_list = []
  for path, dirs, files in os.walk(root):
    for name in files:
      filename = os.path.join(path, name) #get fullpath
      filename = re.sub(re_root, "", filename) #remove root dir from fullpath
      result_list.append(filename)
  return result_list

def os_only_name(filename):
  return os.path.splitext(os.path.split(filename)[1])[0]

def get_src_list(root="."):
  re_src_mask = re.compile(globals()["config"]["src_mask"])
  files = walk_by_root(root)
  files = [ f for f in files if re.match(re_src_mask,f) ] #get only src/main (no tests)
  return files

def get_src_dict_key(filename):
  filename = ""+filename #clone str
  for i in globals()["config"]["path_replaces"]:
    filename = re.sub(re.compile(i["from"]), i["to"], filename)
    #filename = re.sub(re.escape(i["from"]), i["to"], filename)
  return filename

def get_src_dict(root):
  return {get_src_dict_key(f):{"rel_path":f} for f in get_src_list(root)}

def to_json(obj,filename=".json"):
  with open(filename,"w", encoding="utf-8") as f:
    json.dump(obj, f, indent=1, ensure_ascii=False)

def read_lines(filename):
  try:
    with open(filename,"r", encoding="utf-8") as f:
      return [re.sub(r"[\r\n]+$","",line) for line in f.readlines()] # Убрираем переводы сторок
  except UnicodeDecodeError:
    with open(filename,"r", encoding="windows-1251") as f:
      return [re.sub(r"[\r\n]+$","",line) for line in f.readlines()] # Убрираем переводы сторок

def line_replace(s:str) -> str:
    _line_replaces_compiled = list(map(lambda r: {"from":re.compile(r["from"]), "to":r["to"]}, globals()["config"]["line_replaces"]))
    for r in _line_replaces_compiled:
      s = re.sub(r["from"], r["to"], s)
    return s

def add_info(_files,root):
  #to_json(_files,"_files.dbg")
  for f in _files:
    #print(f)
    lines = read_lines(os.path.join(root,_files[f]["rel_path"]))
    #lines = [i for i in lines if not re.match(r"^\s*(package|import)\s+.*$|^\s*$", i)] # Чистим строки с именем пакета, импорты, пустые строки
    lines = [i for i in map(line_replace, lines) if i != "" ] # производим замену строк и берём только не пустые строки
    _files[f].update({
      "lines":lines,
      #"hashs":[hash(i) for i in lines], # построчные хэши
      "hash":hash("".join(lines)), # общий хеш файла, без учёта переводов строк
      "lines_count":len(lines),
      "chars_count":ft.reduce(lambda o,i: o+len(i), lines, 0), # количество байт в строках, без учёта перевода строк. не соответствует длинне файла в байтах
    })

def src(source_type_filename:str, source_location_root:str, src_filename:str=None)->object:
  """
  Сканирование исходников во внутреннюю структуру представления

  @param source_type_filename: Конфигурация исходных файлов.

  @param source_location_root: Корневая директория проекта.

  @param src_filename: Не обязатедьный. Файл для сохранения структуры.
  """
  src = {}
  globals()["config"] = config_json.load(source_type_filename)
  src["source_type"]=os_only_name(source_type_filename)
  src["source_location_root"]=source_location_root

  files = get_src_dict(source_location_root)
  add_info(files, root=source_location_root)
  src["files"] = files
  if src_filename:
    to_json(src,src_filename)
  return src

if __name__ == "__main__":
  cfg = "py.cfg"
  source_location_root = "."
  src_filename = "this.src"

  if len(sys.argv) > 1:
    cfg = sys.argv[1]
  if len(sys.argv) > 2:
    source_location_root = sys.argv[2]
    src_filename = os_only_name(source_location_root)+".src"
  if len(sys.argv) > 3:
    src_filename = sys.argv[3]

  src(cfg, source_location_root, src_filename)

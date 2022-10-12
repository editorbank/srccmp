import json
import re
import os
import base64
import types

# Функции кодирования и декодирования параметорв, сейчас просто base64, но в будущем агоритм может быть заменён.
encode = lambda s: base64.b64encode(s.encode()).decode()
decode = lambda s: base64.b64decode(s.encode()).decode()

# Замена последовательности ${VAR_NAME} на значение переменной окружения VAR_NAME. Tесли таковой переменной в сиситеме нет, тогда подставляется пустая строка без возникновения ошибки.
# Возможно дополнительно указать функцию преобразования ${VAR_NAME:func_name}. Функцией преобразования может быть любая глобальная функция. Если имя функции указано неправильно, то преобразования не происходит.
def env(s:str):
    shell_variables = r"[$][{](.*?)(:(.*?))?[}]"
    def shell_variables_replace(x):
        var_name = x.group(1)
        func_name = x.group(3)
        result = ""
        if var_name in os.environ:
            result = os.environ[var_name]
        if func_name in globals() and isinstance(globals()[func_name],types.FunctionType):
            result = globals()[func_name](result)
        return result
    return re.sub(shell_variables, shell_variables_replace, s)

def loads(s:str):
    C_multiline_comments = r"(?s)[/][*](.)*?[*][/]" #flags=re.DOTALL
    C_or_Python_oneline_comments = r"(?m)^\s*([/][/]|[#])(.)*$" #flags=re.MULTILINE
    leave_only_line_breaks = lambda x:re.sub(r"[^\r\n]", "", x.group(0))

    s = re.sub(C_multiline_comments, leave_only_line_breaks, s)
    s = re.sub(C_or_Python_oneline_comments, leave_only_line_breaks, s)
    s = env(s)
    #print("===%s==="%s)
    return json.loads(s)

# Загрузка небольшого файла JSON с комментариями и заменой значений из переменных среды окружения
# предполагается использовать для загрузки конфигурационных файлов:
# import config_json
# cfg = config_json.load("config.json")

def load(filename:str):
    with open(filename, "r") as f:
        return loads(f.read())


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] in globals():
        print(globals()[sys.argv[1]](sys.argv[2]))
    else:
        print("Use: python -m <function> <argument>")

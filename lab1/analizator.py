import tkinter as tk
from tkinter import filedialog, messagebox, ttk

KEYWORDS_JAVA = {"if", "else", "while", "for", "return", "String", "int", "float", "double", "boolean", "class", "public", "private", "static", "void", "char", "new", "this", "true", "false", "null", "break", "continue"}
OPERATORS_JAVA = {"+", "-", "*", "/", "=", "==", "<", ">", "<=", ">=", "!=", "&&", "||", "++", "--"}
DELIMITERS = {";", ",", "{", "}", "(", ")", "[", "]", ".", "@", "\n", "\t"}

tables = {
    "Ключевые слова": {},
    "Идентификаторы": {},
    "Переменные": {},
    "Числовые константы": {},
    "Строковые константы": {},
    "Операции": {},
    "Разделители": {}
}

category_prefixes = {
    "Ключевые слова": "W",
    "Идентификаторы": "I",
    "Переменные": "V",
    "Числовые константы": "N",
    "Строковые константы": "S",
    "Операции": "O",
    "Разделители": "R"
}

is_array = {}
def add_to_table(table_name, value):
    if value not in tables[table_name]:
        tables[table_name][value] = len(tables[table_name]) + 1
    return f"{category_prefixes[table_name]}{tables[table_name][value]}"

def lexer(code):
    result = []
    i = 0
    prev_token = None
    is_declaring_variable = False
    is_declaring_array = False
    while i < len(code):
        char = code[i]

        if char == ' ':
            i += 1
            continue

        if char == '\t':
            result.append((add_to_table("Разделители", repr(char)), "\\t"))
            i += 1
            continue

        if char == '\n':
            result.append((add_to_table("Разделители", repr(char)), "\\n"))
            i += 1
            continue

        # Обработка комментариев
        if char == '/' and i + 1 < len(code) and code[i + 1] == '/':
            # Пропускаем всё до конца строки
            while i < len(code) and code[i] != '\n':
                i += 1
            continue

        # Обработка многострочных комментариев (/* ... */)
        if char == '/' and i + 1 < len(code) and code[i + 1] == '*':
            i += 2  # Пропускаем /*
            while i + 1 < len(code) and not (code[i] == '*' and code[i + 1] == '/'):
                i += 1
            if i + 1 < len(code):
                i += 2
            continue

        # Строковые константы (двойные кавычки)
        if char == '"':
            start = i
            i += 1
            while i < len(code) and code[i] != '"':
                i += 1
            value = code[start:i+1]
            result.append((add_to_table("Строковые константы", value), value))
            i += 1
            continue

        # Строковые константы (одинарные кавычки)
        if char == "'":
            start = i
            i += 1
            while i < len(code) and code[i] != "'":
                i += 1
            value = code[start:i+1]
            result.append((add_to_table("Строковые константы", value), value))
            i += 1
            continue

        # Числовые константы
        if char.isdigit():
            start = i
            while i < len(code) and (code[i].isdigit() or code[i] == '.'):
                i += 1
            value = code[start:i]
            result.append((add_to_table("Числовые константы", value), value))
            continue

        # Ключевые слова, идентификаторы и переменные
        if char.isalpha() or char == '_':
            start = i
            while i < len(code) and (code[i].isalnum() or code[i] == '_'):
                i += 1
            value = code[start:i]
            if value in KEYWORDS_JAVA:
                result.append((add_to_table("Ключевые слова", value), value))
                
                if value in {"int", "String", "float", "double", "boolean", "char"}:
                    if i < len(code) and code[i] == '[':
                        is_declaring_array = True
                    else:
                        is_declaring_variable = True
            else:
                if is_declaring_variable:
                    if value not in tables["Переменные"]:
                        result.append((add_to_table("Переменные", value), value))
                    is_declaring_variable = False
                elif is_declaring_array:
                    if value not in tables["Переменные"]:
                        result.append((add_to_table("Переменные", value), f"{value}[]"))
                        is_array[value] = True
                    is_declaring_array = False

                # Проверяем, есть ли уже такая переменная в таблице
                if value in tables["Переменные"]:
                    result.append((f"V{tables['Переменные'][value]}", value))
                else:
                    result.append((add_to_table("Идентификаторы", value), value))

            continue

        # Операции
        for op in sorted(OPERATORS_JAVA, key=len, reverse=True):
            if code[i:].startswith(op):
                result.append((add_to_table("Операции", op), op))
                i += len(op)
                break
        else:
            # Разделители (оставшиеся символы)
            for delim in sorted(DELIMITERS, key=len, reverse=True):
                if code[i:].startswith(delim):
                    result.append((add_to_table("Разделители", delim), delim))
                    i += len(delim)
                    break
            else:
                print(f"Неизвестный символ: {repr(char)}")
                raise SyntaxError(f"Неизвестный символ: {repr(char)}")
    filtered_result = []
    prev_token = None
    for token in result:
        if prev_token and prev_token[0].startswith("V") and prev_token[0] == token[0]:
            continue  # Пропускаем этот токен, если он совпадает с предыдущим
        filtered_result.append(token)
        prev_token = token

    return filtered_result


def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                code = file.read()
                code_text.delete(1.0, tk.END)
                code_text.insert(tk.END, code)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при чтении файла: {e}")

def analyze_code():
    code = code_text.get(1.0, tk.END)
    if code.endswith("\n"):
        code = code[:-1]
    result = lexer(code)

    with open("result.txt", "w", encoding="utf-8") as token_file:
        for token in result:
            token_file.write(f"{token[0]}: {token[1]}\n")

    with open("tables_result.txt", "w", encoding="utf-8") as table_file:
        for table_name, table in tables.items():
            table_file.write(f"{table_name}:\n")
            for value, index in table.items():
                if table_name == "Переменные" and value in is_array:
                 table_file.write(f"{category_prefixes[table_name]}{index} : {value}[]\n")
                else:
                 table_file.write(f"{category_prefixes[table_name]}{index} : {value}\n")
            table_file.write("\n")

    result_text.delete(1.0, tk.END)
    for token in result:
        if token[1] == '\\n':
            result_text.insert(tk.END, "\n")
        else:
            result_text.insert(tk.END, f"{token[0]} ")

root = tk.Tk()
root.title("Разработка транслятора")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

tab1 = tk.Frame(notebook)
notebook.add(tab1, text="Анализатор")

left_frame = tk.Frame(tab1)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right_frame = tk.Frame(tab1)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

code_text = tk.Text(left_frame, width=70, height=30, wrap=tk.NONE)
code_text.pack(fill=tk.BOTH, expand=True)

load_button = tk.Button(left_frame, text="Загрузить файл", command=open_file)
load_button.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

result_text = tk.Text(right_frame, width=70, height=30, wrap=tk.NONE)
result_text.pack(fill=tk.BOTH, expand=True)

analyze_button = tk.Button(right_frame, text="Запустить анализатор", command=analyze_code)
analyze_button.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

root.mainloop()
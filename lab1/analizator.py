import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re

KEYWORDS_JAVA = {"if", "else", "while", "for", "return", "String", "int", "float", "double", "boolean", "class", "public", "private", "static", "void", "char", "new", "this", "true", "false", "null", "break", "continue"}
OPERATORS_JAVA = {"+", "-", "*", "/", "=", "==", "<", ">", "<=", ">=", "!=", "&&", "||", "++", "--"}
DELIMITERS = {";", ",", "{", "}", "(", ")", "[", "]", ".", "@", "\n", "\t"}

TOKEN_PATTERNS = [
    (r"\b\d+(\.\d+)?\b", "Числовые константы"),
    (r'".*?"', "Строковые константы"),
    (r"\b[a-zA-Z_][a-zA0-9_]*\b", "Идентификаторы"),
]

# Таблицы лексем
tables = {
    "Ключевые слова": {},
    "Идентификаторы": {},
    "Числовые константы": {},
    "Строковые константы": {},
    "Операции": {},
    "Разделители": {}
}

# Префиксы категорий
category_prefixes = {
    "Ключевые слова": "W",
    "Идентификаторы": "I",
    "Числовые константы": "N",
    "Строковые константы": "S",
    "Операции": "O",
    "Разделители": "R"
}

def add_to_table(table_name, value):
    if value not in tables[table_name]:
        tables[table_name][value] = len(tables[table_name]) + 1
    return f"{category_prefixes[table_name]}{tables[table_name][value]}"


def lexer(code):
    result = []
    while code:
        if code.startswith("    "):
            result.append((add_to_table("Разделители", repr("\t")), "\\t"))
            code = code[4:]
            continue
        if code[0] == "\n":
            result.append((add_to_table("Разделители", repr(code[0])), "\\n"))
            code = code[1:]
            continue
        if code[0] == " ":
            code = code[1:]
            continue

        match = None

        # Пропуск строк, начинающихся с #
        if code.startswith("#"):
            code = code[code.find("\n") + 1:] if "\n" in code else ""
            continue

        # Проверяем ключевые слова, идентификаторы, числа и строки
        for pattern, token_type in TOKEN_PATTERNS:
            match = re.match(pattern, code)
            if match:
                value = match.group(0)
                if value in KEYWORDS_JAVA:
                    result.append((add_to_table("Ключевые слова", value), value))
                else:
                    result.append((add_to_table(token_type, value), value))
                break

        # Проверяем операции
        if not match:
            for op in sorted(OPERATORS_JAVA, key=len, reverse=True):
                if code.startswith(op):
                    result.append((add_to_table("Операции", op), op))
                    match = op
                    break

        # Проверяем разделители
        if not match:
            for delim in DELIMITERS:
                if code.startswith(delim):
                    result.append((add_to_table("Разделители", delim), delim))
                    match = delim
                    break

        # Удаление обработанного кода
        if match:
            code = code[len(match):] if isinstance(match, str) else code[len(match.group(0)):]

        else:
            print(f"Неизвестный символ: {repr(code[0])}")
            raise SyntaxError(f"Неизвестный символ: {repr(code[0])}")

    return result

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
                table_file.write(f"{category_prefixes[table_name]}{index} : {value}\n")
            table_file.write("\n")


    result_text.delete(1.0, tk.END)
    lines = code.splitlines(keepends=True)

    index_lines = []
    for line in lines:
        tokens = lexer(line)
        token_indices = []
        for token in tokens:
            token_indices.append(token[0])

        index_lines.append(" ".join(token_indices))

    result_text.insert(tk.END, "\n".join(index_lines))

root = tk.Tk()
root.title("Лексический анализатор")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

tab1 = tk.Frame(notebook)
notebook.add(tab1, text="Лексический анализатор")

left_frame = tk.Frame(tab1)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right_frame = tk.Frame(tab1)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

code_text = tk.Text(left_frame, width=60, height=20, wrap=tk.NONE)
code_text.pack(fill=tk.BOTH, expand=True)

load_button = tk.Button(left_frame, text="Загрузить файл", command=open_file)
load_button.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

result_text = tk.Text(right_frame, width=60, height=20, wrap=tk.NONE)
result_text.pack(fill=tk.BOTH, expand=True)

analyze_button = tk.Button(right_frame, text="Запустить анализатор", command=analyze_code)
analyze_button.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

root.mainloop()
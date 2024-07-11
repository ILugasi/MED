import json
import os
import datetime
import uuid


MINIMUM_LINE_LENGTH = 45


def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ""


def pad_line(line: str, size: int = MINIMUM_LINE_LENGTH, pad_chr: chr = " ", term_chr: chr = "|") -> str:
    if is_entirely_char(line) and line[0] != term_chr:
        return size * line[0] + "\n"
    return line + (size - len(line)) * pad_chr + term_chr + "\n"
    

def pad_text(text: str, pad_chr: chr = ' ', term_chr: chr = '|'):
    new_text = ""
    max_len = longest_line_length(text)
    if max_len + 2 < MINIMUM_LINE_LENGTH:
        max_len = MINIMUM_LINE_LENGTH
    else:
        max_len = max_len + 2
    for line in text.splitlines():
        line = line.strip()
        if line == "":
            continue
        new_text += pad_line(line=line, size=max_len, pad_chr=pad_chr, term_chr=term_chr)
    return new_text


def replace_template_elements(template_text: str, key_map: dict):
    for key, value in key_map.items():
        if f"<<{key}>>" in template_text:
            text = ""
            for line in value.split("\n"):
                text += f"|     {line}\n"
            template_text = template_text.replace(f"<<{key}>>", text)
        elif f"<{key}>" in template_text:
            template_text = template_text.replace(f"<{key}>", str(value))
    return template_text


def is_entirely_char(s):
    return all(c == s[0] for c in s)


def longest_line_length(text):
    lines = text.split('\n')
    return max(len(line) for line in lines)


def clear_screen():
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For macOS and Linux
    else:
        os.system('clear')


def get_base_path():
    return os.path.dirname(os.path.abspath(__file__))


def get_outputs_folder():
    base_path = get_base_path()
    return os.path.join(base_path, "outputs")


def create_folder():
    outputs_folder = get_outputs_folder()
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    unique_id = str(uuid.uuid4())
    folder_name = f"{current_datetime}_{unique_id}"
    full_path = os.path.join(outputs_folder, folder_name)
    os.makedirs(full_path)
    return full_path


def save_json_to_folder(data: dict, folder_path: str, filename: str):
    file_path = os.path.join(folder_path, filename)

    # Save the data to the file
    with open(file_path, 'w') as file:
        file.write(json.dumps(data))

    return file_path


def load_json_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return None


def format_results(results: dict):
    for result in results:
        result["Hexdump"] = prettify_hexdump(result["Hexdump"])
        result["Disassembly"] = prettify_disassembly(result["Disassembly"])
    return results


def prettify_hexdump(hexdump_dict: dict):
    text = ""
    for entry in hexdump_dict:
        address = entry['address']
        hex_code = entry['hex']
        char_repr = entry['char']
        text += f"{address.replace('L', '').zfill(18)}  {hex_code.ljust(47)}   {char_repr}\n"
    return text


def prettify_disassembly(disassembly_dict: dict):
    text = ""
    for entry in disassembly_dict:
        address = entry['address']
        hex_code = entry['hex']
        instruction = entry['instruction']
        text += f"{address.replace('L', '').zfill(18)} {hex_code.ljust(16)} {instruction}\n"
    return text


def get_folder_names(directory):
    try:
        entries = os.listdir(directory)
        folder_names = [entry for entry in entries if os.path.isdir(os.path.join(directory, entry))]
        reversed_list = folder_names[::-1]
        return reversed_list
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def convert_folder_format(entry):
    datetime_str, uuid_str = entry.rsplit('_', 1)
    dt_object = datetime.datetime.strptime(datetime_str, '%Y-%m-%d_%H-%M-%S')
    new_datetime_format = dt_object.strftime('%H:%M:%S %d/%m/%Y')
    return f"{new_datetime_format} - {uuid_str}"

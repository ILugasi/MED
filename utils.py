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
    
def padLine(line:str,size:int = MINIMUM_LINE_LENGTH,padd_chr:chr = " ",term_chr:chr = "|") -> str:
    if is_entirely_char(line) and line[0] != term_chr:
        return size * line[0] + "\n"
    return line + (size - len(line)) * padd_chr + term_chr + "\n"
    

def padText(text:str,padd_chr:chr = ' ',term_chr:chr = '|'):
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
        new_text += padLine(line=line,size=max_len, padd_chr=padd_chr,term_chr=term_chr)
    return new_text

def replaceTemplateElements(template_text:str, key_map:dict):
    for key, value in key_map.items():
        template_text = template_text.replace("<" + key + ">", str(value))
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


def create_folder():
    base_path = get_base_path()
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    unique_id = str(uuid.uuid4())
    folder_name = f"{current_datetime}_{unique_id}"
    full_path = os.path.join(base_path, "outputs", folder_name)
    os.makedirs(full_path)
    return full_path


def save_string_data_to_folder(data: str, folder_path: str, filename: str):
    file_path = os.path.join(folder_path, filename)

    # Save the data to the file
    with open(file_path, 'w') as file:
        file.write(data)

    print(f"Data saved to file '{file_path}'.")

    return file_path

def load_json_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return None

def filter_result_json(results):
    for result in results:
        del result["Hexdump"]
        del result["Disassembly"]
    return results
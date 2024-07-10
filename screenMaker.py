
MINIMUM_LINE_LENGTH = 45
def padLine(line:str,size:int = MINIMUM_LINE_LENGTH,padd_chr:chr = " ",term_chr:chr = "|") -> str:
    print(f"{size=}")
    if is_entirely_char(line) and line[0] != term_chr:
        return size * line[0] + "\n"
    return line + (size - len(line)) * padd_chr + term_chr + "\n"
    

def padText(text:str,padd_chr:chr = ' ',term_chr:chr = '|'):
    new_text = ""
    max_len = longest_line_length(text)
    print(f"{max_len=}")
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

def replaceTemplateElements(template_text:str,key_map:dict):
    for key, value in key_map.items():
        template_text = template_text.replace("<" + key + ">", value)
    return template_text

def is_entirely_char(s):
    return all(c == s[0] for c in s)

def longest_line_length(text):
    lines = text.split('\n')
    return max(len(line) for line in lines)

def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ""

main_text = read_file_content("main.md")
data_text = read_file_content("results\\data.md")
options_text = read_file_content("results\\options.md")

data_key_map = {
    'address': '0x12345678',
    'description': 'hi'
}
main_key_map = {
    'main_title': 'fdsasssssssssssssssssssssssss',
    'sub_title': 'b',
    'data': replaceTemplateElements(data_text,data_key_map),
    'options': replaceTemplateElements(options_text,{})
}
print(replaceTemplateElements(main_text,main_key_map))
print(padText(replaceTemplateElements(main_text,main_key_map)))

from typing import Optional

from utils import clear_screen, read_file_content, replaceTemplateElements, padText
from os import path


class ScreenMgmt:
    screens = {}

    def __init__(self, frame_id: str, main_title: str, sub_title: str = ""):
        self.frame_id = frame_id
        self.main_title = main_title
        self.sub_title = sub_title
        self.frame_template_text = read_file_content("frameTemplates/frame.txt")
        self.options = {}

        if frame_id not in ScreenMgmt.screens:
            ScreenMgmt.screens[frame_id] = self
        
    def build_parameters(self, params: dict):
        return {
            'main_title': self.main_title,
            'sub_title': self.build_sub_title(),
            'data': self.build_data(params),
            'options': self.build_options(),
            'option0': self.get_option_0_text()
            }
    
    def build_sub_title(self):
        if self.sub_title:
            template = read_file_content(path.join("frameTemplates", "sub_title.txt"))
            return replaceTemplateElements(template,{'sub_title': self.sub_title})
        else:
            return ""
        
    def build_data(self, input_params: None):
        data = ""
        template = read_file_content(path.join("frameTemplates", self.frame_id, "data.txt"))
        
        params = self.build_data_replace_params(input_params)
        if isinstance(params,dict):
            list_params = [params]
        else:
            list_params = params

        for single_replace_params in list_params:
            data += replaceTemplateElements(template,single_replace_params) + "\n"

        return data

    def build_data_replace_params(self, input_params: Optional[dict]):
        return {}
    
    def build_options(self):
        self.options = self.build_options_params()
        i = 1
        options_text = ""
        options_template = read_file_content(path.join("frameTemplates", "option.txt"))
        for option_description in self.options.keys():
            index_description_replace_params = {
                'index': str(i),
                'description': option_description
            }
            options_text += replaceTemplateElements(options_template,index_description_replace_params) + "\n"
            i += 1                                                    
        return options_text

    def build_options_params(self):
        return {}

    def build_screen(self, params: dict):
        return replaceTemplateElements(self.frame_template_text, self.build_parameters(params))

    def print_screen(self, params: dict):
        clear_screen()
        print(padText(self.build_screen(params)))
        self.get_input_options()

    def get_input_options(self):
        amount_options = len(self.options)
        keys_list = list(self.options.keys())
        while True:
            user_input = input()
            try:
                choice = int(user_input)
                if choice == 0:
                    self.option0()
                elif 1 <= choice <= amount_options:
                    selected_key = keys_list[choice - 1]
                    selected_function = self.options[selected_key]
                    selected_function()
                else:
                    print(f"Error: The number is not in the options.")
            except ValueError:
                print("Error: Input is not a valid number. Please try again.")

    @staticmethod
    def get_screen(frame_id: str, params: dict = None):
        ScreenMgmt.screens[frame_id].print_screen(params)

    def option0(self):
        ScreenMgmt.get_screen("main")
    
    def get_option_0_text(self):
        return "Return to Menu"


    

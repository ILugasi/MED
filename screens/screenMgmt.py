from utils import clear_screen, read_file_content, replace_template_elements, pad_text
from os import path


class ScreenMgmt:
    screens = {}

    def __init__(self, frame_id: str, main_title: str, sub_title: str = ""):
        self.frame_id = frame_id
        self.main_title = main_title
        self.sub_title = sub_title
        self.frame_template_text = read_file_content("frameTemplates/frame.txt")
        self.options = {}
        self.passed_params = {}

        if frame_id not in ScreenMgmt.screens:
            ScreenMgmt.screens[frame_id] = self
        
    def build_parameters(self):
        return {
            'main_title': self.main_title,
            'sub_title': self.build_sub_title(),
            'data': self.build_data(),
            'options': self.build_options(),
            'option0': self.get_option_0_text()
            }
    
    def build_sub_title(self):
        if self.sub_title:
            template = read_file_content(path.join("frameTemplates", "sub_title.txt"))
            return replace_template_elements(template, {'sub_title': self.sub_title})
        else:
            return ""
        
    def build_data(self):
        data = ""

        params = self.build_data_replace_params()
        if isinstance(params, dict):
            list_params = [params]
        else:
            list_params = params

        if not list_params:
            template = read_file_content(path.join("frameTemplates", "no_result.txt"))
            no_result_params = {"no_result": self.get_no_result_text()}
            return replace_template_elements(template, no_result_params)

        template = read_file_content(path.join("frameTemplates", self.frame_id, "data.txt"))
        for single_replace_params in list_params:
            data += replace_template_elements(template, single_replace_params) + "\n"

        return data

    def build_data_replace_params(self):
        return {}
    
    def build_options(self):
        self.options = self.build_options_params()
        if self.is_options_choice():
            list_options = self.options.keys()
        else:
            list_options = self.options
        i = 1
        options_text = ""
        options_template = read_file_content(path.join("frameTemplates", "option.txt"))
        for option_description in list_options:
            index_description_replace_params = {
                'index': str(i),
                'description': option_description
            }
            options_text += replace_template_elements(options_template, index_description_replace_params) + "\n"
            i += 1                                                    
        return options_text

    def build_options_params(self):
        return {}

    def build_screen(self):
        return replace_template_elements(self.frame_template_text, self.build_parameters())

    def print_screen(self, passed_params: dict):
        if passed_params:
            self.passed_params = passed_params
        frame = pad_text(self.build_screen())
        clear_screen()
        print(frame)
        self.get_input()

    def get_input_list_choice(self, list_options: list):
        amount_options = len(list_options)
        while True:
            user_input = input()
            try:
                choice = int(user_input)
                if choice == 0:
                    self.option0()
                elif 1 <= choice <= amount_options:
                    return list_options[choice-1]
                else:
                    print(f"Error: The number is not in the options.")
            except ValueError:
                print("Error: Input is not a valid number. Please try again.")

    def get_input(self):
        if self.is_options_choice():
            choice = self.get_input_list_choice(list(self.options.keys()))
            self.options[choice]()
        else:
            choice = self.get_input_list_choice(self.build_list_options())
            self.run_list_option_func(choice)

    @staticmethod
    def get_no_result_text():
        return ""

    @staticmethod
    def get_screen(frame_id: str, params: dict = None):
        ScreenMgmt.screens[frame_id].print_screen(params)

    @staticmethod
    def option0():
        ScreenMgmt.get_screen("main")

    @staticmethod
    def get_option_0_text():
        return "Return to Menu"

    @staticmethod
    def is_options_choice():
        return True

    def run_list_option_func(self, choice: str):
        pass

    @staticmethod
    def build_list_options():
        return []


    

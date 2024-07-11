import os

from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta
from utils import get_outputs_folder, get_folder_names, convert_folder_format


class ScreenBrowseResults(ScreenMgmt, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(frame_id="browse_results", main_title="Browse Results", sub_title="")

    @staticmethod
    def build_list_options():
        outputs_folder = get_outputs_folder()
        folders = get_folder_names(outputs_folder)
        return folders

    @staticmethod
    def is_options_choice():
        return False

    def build_options_params(self):
        folders = self.build_list_options()
        return self.format_folders(folders)

    def run_list_option_func(self, choice: str):
        outputs_folder = get_outputs_folder()
        result_folder_path = os.path.join(outputs_folder, choice)
        self.passed_params["out_folder"] = result_folder_path
        ScreenMgmt.get_screen("results", self.passed_params)

    @staticmethod
    def format_folders(list_folders: list):
        return [convert_folder_format(entry) for entry in list_folders]

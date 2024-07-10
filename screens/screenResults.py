import os

from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta
from utils import load_json_from_file, filter_result_json


class ScreenResults(ScreenMgmt, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(frame_id="results", main_title="Results", sub_title="Sub Results")
        self.last_out_folder = None

    def build_data_replace_params(self, input_params: dict):
        self.last_out_folder = input_params.get("out_folder")
        results_file = os.path.join(self.last_out_folder, "results.json")
        data = load_json_from_file(results_file)
        return filter_result_json(data)

    def build_options_params(self):
        return {
            'Upload results to VT': self.upload_results_to_vt
        }

    def upload_results_to_vt(self):
        # Todo: Lugasi, do your magic here, self.last_out_folder is the results
        print(self.last_out_folder)


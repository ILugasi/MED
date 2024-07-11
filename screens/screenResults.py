import os

from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta
from utils import load_json_from_file, filter_result_json
from analyzers import  vt
from utils import load_json_from_file


class ScreenResults(ScreenMgmt, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(frame_id="results", main_title="Results", sub_title="")
        self.current_results = None

    def build_data_replace_params(self):
        out_folder = self.passed_params.get("out_folder")
        results_file = os.path.join(out_folder, "results.json")
        self.current_results = load_json_from_file(results_file)
        return self.current_results

    def build_options_params(self):
        return {
            'Upload results to VT': self.upload_results_to_vt,
            'Peek': self.peek
        }

    def upload_results_to_vt(self):
        # Todo: Lugasi, do your magic here, self.last_out_folder is the results
        print(vt.analyze(self.last_out_folder))

    def peek(self):
        self.passed_params["results"] = self.current_results
        ScreenMgmt.get_screen("peek", self.passed_params)

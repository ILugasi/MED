import os

from analyzers import vt
from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta
from utils import load_json_from_file


class ScreenVT(ScreenMgmt, metaclass=SingletonMeta):

    def __init__(self):
        super().__init__(frame_id="vt", main_title="VirusTotal", sub_title="")

    def get_vt_results_path(self):
        return os.path.join(self.passed_params.get("out_folder"), vt.VT_RESULTS_FILE)

    def is_results_available(self):
        return os.path.exists(self.get_vt_results_path())

    def load_vt_results(self):
        if not self.is_results_available():
            self.analyze()
        return load_json_from_file(self.get_vt_results_path())

    def analyze(self):
        vt.analyze(self.passed_params.get("out_folder"))

    def build_data_replace_params(self):

        return self.load_vt_results()

    def build_options_params(self):
        return {
            'Rescan': self.rescan,
            'Return': self.return_option,
        }

    def rescan(self):
        self.analyze()
        self.print_screen(self.passed_params)

    def return_option(self):
        ScreenMgmt.get_screen("results", self.passed_params)

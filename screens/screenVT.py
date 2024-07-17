import subprocess
import threading

from analyzers import vt
from animation.loadingAnimation import loading_screen
from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta


class ScreenVT(ScreenMgmt, metaclass=SingletonMeta):

    def __init__(self):
        super().__init__(frame_id="vt", main_title="VirusTotal", sub_title="")

    def build_data_replace_params(self):
        result = vt.analyze(self.passed_params.get("out_folder"))
        params = {"VT": result}
        return params

    def build_options_params(self):
        return {
            'Return': self.return_option,
        }

    def return_option(self):
        ScreenMgmt.get_screen("results", self.passed_params)

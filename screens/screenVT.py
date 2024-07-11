from analyzers import vt
from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta


class ScreenVT(ScreenMgmt, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(frame_id="vt", main_title="VirusTotal", sub_title="")

    def build_data_replace_params(self):
        params = {"VT": vt.analyze(self.passed_params.get("out_folder"))}
        return params

    def build_options_params(self):
        return {
            'Return': self.return_option,
        }

    def return_option(self):
        ScreenMgmt.get_screen("results", self.passed_params)

import threading

from analyzers import vt
from animation.loadingAnimation import loading_screen
from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta

result = ""


class ScreenVT(ScreenMgmt, metaclass=SingletonMeta):

    def __init__(self):
        super().__init__(frame_id="vt", main_title="VirusTotal", sub_title="")

    def build_data_replace_params(self):
        output_thread = threading.Thread(target=self.run_vt, args=(self.passed_params.get("out_folder"),))
        output_thread.start()
        loading_screen(output_thread)
        output_thread.join()
        params = {"VT": result}
        return params

    def build_options_params(self):
        return {
            'Return': self.return_option,
        }

    @staticmethod
    def run_vt(folder_to_scan):
        global result
        result = vt.analyze(folder_to_scan)

    def return_option(self):
        ScreenMgmt.get_screen("results", self.passed_params)

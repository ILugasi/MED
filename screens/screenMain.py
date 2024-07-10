from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta


class ScreenMain(ScreenMgmt, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(frame_id="main", main_title="Main", sub_title="MED")

    def build_options_params(self):
        return {
            'Start Scan': self.start_scan,
            'Results': self.results_page,
            'About': self.about_us_page,
            
        }

    @staticmethod
    def start_scan():
        ScreenMgmt.get_screen("start_scan")

    @staticmethod
    def about_us_page():
        ScreenMgmt.get_screen("about")

    @staticmethod
    def results_page():
        ScreenMgmt.get_screen("results")

    @staticmethod
    def option0():
        ScreenMgmt.get_screen("exit")

    @staticmethod
    def get_option_0_text():
        return "Exit"

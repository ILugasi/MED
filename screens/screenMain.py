from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta


class ScreenMain(ScreenMgmt, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(frame_id="main", main_title="Main", sub_title="DETECTING THE UNDETECTABLE")

    def build_options_params(self):
        return {
            'Start Scan': self.start_scan,
            'Browse Results': self.browse_results_page,
            'Logs': self.logs_page,
            'About': self.about_us_page,
        }

    @staticmethod
    def start_scan():
        ScreenMgmt.get_screen("start_scan")

    @staticmethod
    def about_us_page():
        ScreenMgmt.get_screen("about")

    @staticmethod
    def browse_results_page():
        ScreenMgmt.get_screen("browse_results")

    @staticmethod
    def logs_page():
        ScreenMgmt.get_screen("logs")

    @staticmethod
    def option0():
        ScreenMgmt.get_screen("exit")

    @staticmethod
    def get_option_0_text():
        return "Exit"

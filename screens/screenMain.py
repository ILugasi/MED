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
    def start_scan(self):
        ScreenMgmt.get_screen("start_scan")

    def about_us_page(self):
        ScreenMgmt.get_screen("about")
        
    def results_page(self):
        ScreenMgmt.get_screen("results")
    
    def option0(self):
        ScreenMgmt.get_screen("exit")
    
    def get_option_0_text(self):
        return "Exit"

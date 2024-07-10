import sys
from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta


class ScreenExit(ScreenMgmt, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(frame_id="exit", main_title="Exit", sub_title="Are you sure you want to exit?")

    def build_options_params(self):
        return {
            'Exit': self.real_exit
        }
    
    def real_exit(self):
        sys.exit()

from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta

class ScreenWelcome(ScreenMgmt, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(frame_id="welcome", main_title="MED", sub_title="Welcome")
        
        
    def get_option_0_text(self):
        return "Start"

import sys
from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta

class ScreenAbout(ScreenMgmt, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(frame_id="about", main_title="About")



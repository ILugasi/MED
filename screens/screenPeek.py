from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta


class ScreenPeek(ScreenMgmt, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(frame_id="peek", main_title="Peek", sub_title="")

    def build_data_replace_params(self):
        return self.passed_params.get("results")

    def build_options_params(self):
        return {
            'Return': self.return_option,
        }

    def return_option(self):
        ScreenMgmt.get_screen("results", self.passed_params)

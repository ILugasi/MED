import os

from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta
from utils import get_base_path
from configLogger import get_logger_overwrite_path


class ScreenLogs(ScreenMgmt, metaclass=SingletonMeta):

    def __init__(self):
        super().__init__(frame_id="logs", main_title="Logs", sub_title="")


    @staticmethod
    def get_logs_path():
        return os.path.join(get_base_path(), get_logger_overwrite_path())

    def is_logs_available(self):
        return os.path.exists(self.get_logs_path())

    def build_data_replace_params(self):
        if self.is_logs_available():
            with open(self.get_logs_path(), 'r') as file:
                data = file.read()
                return {"logs": data}
        return {"logs": "No logs found"}


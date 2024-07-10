from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta
from utils import create_folder, get_base_path, save_string_data_to_folder

import subprocess
import os


VOLATILITY_TO_BANNER = "Volatility Foundation Volatility Framework 2.6.1" # Move this to another place
class ScreenStartScan(ScreenMgmt, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(frame_id="start_scan", main_title="Start Scan", sub_title="Start a new MED scan")


    def build_options_params(self):
        return {
            'scan dump file': self.scan_dump_file_option
        }
    
    def scan_dump_file_option(self):
        dump_file_path = input("Please enter dump file path: ")
        profile = input("Please enter dump file profile: ")
        self.scan_dump_file(dump_file_path, profile)

    def scan_dump_file(self, dump_file_path: str, profile):
        base_path = get_base_path()
        python2_path = os.getenv("PYTHON2_PATH")
        out_folder_path = create_folder()
        script_path = os.path.join(base_path, "volatility", "vol.py")
        command = 'med'
        cmd = [
            python2_path,
            script_path,
            command,
            '-f', dump_file_path,
            '--profile=' + profile,
            '--output=json',
            '-D', out_folder_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stderr.strip() != VOLATILITY_TO_BANNER:
            print(f"Command resulted error\n"
                  f"Press ENTER to return to the main menu:\n"
                  f"Error: {result.stderr}")
            input()
            return ScreenMgmt.get_screen("main")

        else:
            save_string_data_to_folder(result.stdout, out_folder_path, "results.json")
            params = {"out_folder": out_folder_path}
            ScreenMgmt.get_screen("results", params)



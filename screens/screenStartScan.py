import threading

from animation.loadingAnimation import loading_screen
from consts import VOLATILITY_TOP_BANNER
from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta
from utils import create_folder, get_base_path, save_json_to_folder, format_results

import subprocess
import json
import os

stdout = ""
stderr = ""


class ScreenStartScan(ScreenMgmt, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(frame_id="start_scan", main_title="Start Scan", sub_title="Start a new MED scan")

    def build_options_params(self):
        return {
            'scan dump file': self.scan_dump_file_option
        }
    
    def scan_dump_file_option(self):
        dump_file_path = input("Please enter dump file path: ").strip().strip('"').strip("'")
        profile = input("Please enter dump file profile: ").strip().strip('"').strip("'")
        self.scan_dump_file(dump_file_path, profile)

    @staticmethod
    def run_sub_process(cmd):
        global stdout, stderr
        result = subprocess.run(cmd, capture_output=True, text=True)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

    def scan_dump_file(self, dump_file_path: str, profile):
        global stdout, stderr
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
        output_thread = threading.Thread(target=self.run_sub_process, args=(cmd,))
        output_thread.start()
        loading_screen(output_thread)
        output_thread.join()
        if stderr != VOLATILITY_TOP_BANNER:
            print(f"Command resulted error\n"
                  f"Press ENTER to return to the main menu:\n"
                  f"Error: {stderr}")
            input()
            return ScreenMgmt.get_screen("main")

        else:
            formatted_results = format_results(json.loads(stdout))
            save_json_to_folder(formatted_results, out_folder_path, "results.json")
            self.passed_params["out_folder"] = out_folder_path
            ScreenMgmt.get_screen("results", self.passed_params)

import threading

from animation.loadingAnimation import loading_screen
from consts import VOLATILITY_TOP_BANNER
from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta
from utils import create_folder, get_base_path, save_json_to_folder, format_results

import subprocess
import json
import os
import logging

logger = logging.getLogger(__name__)


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

    def scan_dump_file(self, dump_file_path: str, profile):
        base_path = get_base_path()
        python2_path = os.getenv("PYTHON2_PATH")
        out_folder_path = create_folder()
        # TODO: should be used and passed to MED Module once it's avaialable
        # logger_path = os.path.join(base_path, get_logger_relative_path())
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
        logger.info(f"Starting a MED dump scan on file: '{dump_file_path}' with profile '{profile}'")

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if stderr.strip() != VOLATILITY_TOP_BANNER:
            logger.error(f"MED dump scan resulted error\n"
                         f"Press ENTER to return to the main menu:\n"
                         f"Error: {stderr}")
            input()
            return ScreenMgmt.get_screen("main")

        else:
            formatted_results = format_results(json.loads(stdout))
            logger.info(f"MED dump scan finished successfully, saving results to {out_folder_path}")
            save_json_to_folder(formatted_results, out_folder_path, "results.json")
            self.passed_params["out_folder"] = out_folder_path
            ScreenMgmt.get_screen("results", self.passed_params)

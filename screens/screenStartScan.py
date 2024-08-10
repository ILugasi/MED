import threading

from configLogger import write_to_log_files, get_relative_log_folder
from consts import VOLATILITY_TOP_BANNER, VOLATILITY_LOG_PATH
from screens.screenMgmt import ScreenMgmt
from singletonMeta import SingletonMeta
from utils import create_folder, get_base_path, save_json_to_folder, format_results

import subprocess
import json
import time
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
        self.scan_dump_file(dump_file_path)

    def scan_dump_file(self, dump_file_path: str):
        base_path = get_base_path()
        python_path = os.getenv("PYTHON_PATH")
        out_folder_path = create_folder()
        volatility_log_path = os.path.join(base_path, get_relative_log_folder(), VOLATILITY_LOG_PATH)
        script_path = os.path.join(base_path, "volatility3", "vol.py")
        command = 'windows.med'
        cmd = [
            python_path,
            script_path,
            '-r=json',
            '-o', out_folder_path,
            '-f', dump_file_path,
            command,
            '--dump'
        ]
        logger.info(f"Starting a MED dump scan on file: '{dump_file_path}'")

        # Event to stop the tailing thread
        stop_event = threading.Event()

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                clean_output = output.strip()
                if clean_output:
                    logger.info(clean_output)

        return_code = process.poll()

        stdout = process.stdout.read()

        stop_event.set()

        if return_code != 0:
            logger.error(f"MED dump scan resulted error\n"
                         f"Press ENTER to return to the main menu:\n")
            input()
            return ScreenMgmt.get_screen("main")
        else:
            formatted_results = format_results(json.loads(stdout))
            logger.info(f"MED dump scan finished successfully, saving results to {out_folder_path}")
            save_json_to_folder(formatted_results, out_folder_path, "results.json")
            self.passed_params["out_folder"] = out_folder_path
            ScreenMgmt.get_screen("results", self.passed_params)

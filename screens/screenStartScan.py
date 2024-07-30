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
        profile = input("Please enter dump file profile: ").strip().strip('"').strip("'")
        self.scan_dump_file(dump_file_path, profile)

    @staticmethod
    def tail(file_path, stop_event):
        with open(file_path, 'r') as volatility_log_file:
            # Move the pointer to the end of the file
            volatility_log_file.seek(0, 2)

            while not stop_event.is_set():
                line = volatility_log_file.readline()
                if not line:
                    time.sleep(0.1)  # Sleep briefly
                    continue

                print(line, end='')
                write_to_log_files(line)

    def scan_dump_file(self, dump_file_path: str, profile):
        base_path = get_base_path()
        python2_path = os.getenv("PYTHON2_PATH")
        out_folder_path = create_folder()
        volatility_log_path = os.path.join(base_path, get_relative_log_folder(), VOLATILITY_LOG_PATH)
        script_path = os.path.join(base_path, "volatility", "vol.py")
        command = 'med'
        cmd = [
            python2_path,
            script_path,
            command,
            '-f', dump_file_path,
            '--profile=' + profile,
            '--output=json',
            '-D', out_folder_path,
            '-Q', volatility_log_path
        ]
        logger.info(f"Starting a MED dump scan on file: '{dump_file_path}' with profile '{profile}'")

        # Event to stop the tailing thread
        stop_event = threading.Event()

        # Start the tailing thread
        tail_thread = threading.Thread(target=self.tail, args=(volatility_log_path, stop_event))
        tail_thread.start()

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        stop_event.set()
        tail_thread.join()

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

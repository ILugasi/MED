import argparse
from datetime import datetime

import requests
import time
import os
import glob
from dotenv import load_dotenv

import logging

from utils import save_json_to_folder

logger = logging.getLogger(__name__)
load_dotenv()
API_KEY = os.getenv('VT_API_KEY')
VT_RESULTS_FILE = "vt_results.txt"


def get_dnr_files(directory):
    pattern = os.path.join(directory, '*.dmp')
    dnr_files = glob.glob(pattern)
    return dnr_files


def analyze(directory):
    if not API_KEY:
        input("Couldn't find ENV variable VT_API_KEY, press ENTER to return")
        return None
    files = get_dnr_files(directory)
    ids = {}
    ret = ""
    for file in files:
        ids[upload_file(file)] = os.path.basename(file)
    for file_id in ids.keys():
        found = False
        results = get_scan_results(file_id)
        for key, value in results.items():
            if value['result'] is not None:
                ret += f"{ids[file_id]}:{value['engine_name']} detects {value['category']} with {value['result']}\n"
                found = True
        if not found:
            ret += f"{ids[file_id]}:no detection found\n"

    now = datetime.now().strftime('%H:%M:%S %d/%m/%Y')
    results = {
        "last_scan_date": now,
        "results": ret
    }
    logger.info(f"Saving VT results to folder '{directory}', file: {VT_RESULTS_FILE}")
    save_json_to_folder(results, directory, VT_RESULTS_FILE)


def upload_file(file_path):
    url = 'https://www.virustotal.com/api/v3/files'
    headers = {
        'X-Apikey': API_KEY
    }
    files = {'file': (file_path, open(file_path, 'rb'))}
    logger.info(f'uploading {file_path}')
    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        file_id = response.json()['data']['id']
        return file_id
    else:
        print(f"Error uploading file: {response.status_code}")
        print(response.json())
        input("press ENTER to return")
        return None


def get_scan_results(file_id):
    url = f'https://www.virustotal.com/api/v3/analyses/{file_id}'
    headers = {
        'X-Apikey': API_KEY
    }
    logger.info(f"querying results from url: '{url}'. This may take few minutes")
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result['data']['attributes']['status'] == 'completed':
                return result['data']['attributes']['results']
            else:
                # print("Scan in progress, waiting for 10 seconds...")
                time.sleep(10)
        else:
            logger.error(f"Error getting scan results: {response.status_code}:\n{response.json()}")
            input("press ENTER to return")
            return None


def main():
    parser = argparse.ArgumentParser(description="Upload a file to VirusTotal and get the scan results.")
    parser.add_argument('directory', type=str, help="The path to the file to be scanned.")

    args = parser.parse_args()
    logger.info(analyze(args.directory))
    file_id = upload_file(args.file_path)
    if file_id:
        results = get_scan_results(file_id)
        if results:
            logger.info(results)


if __name__ == '__main__':
    main()

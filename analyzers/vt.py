import argparse
import requests
import time
import os
import glob
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('API_KEY')


def get_dnr_files(directory):
    pattern = os.path.join(directory, '*.dnr')
    dnr_files = glob.glob(pattern)
    return dnr_files


def analyze(directory):
    files = get_dnr_files(directory)
    ids={}
    ret=""
    for file in files:
        ids[upload_file(file)]=os.path.basename(file)
    for file_id in ids.keys():
        found=False
        results = get_scan_results(file_id)
        for key, value in results.items():
            if value['result'] is not None:
                ret+=f"{ids[file_id]}:{value['engine_name']} detects {value['category']} with {value['result']}\n"
                found=True
        if not found:
            ret+=f"{ids[file_id]}:no detection found\n"
    return ret


def upload_file(file_path):
    url = 'https://www.virustotal.com/api/v3/files'
    headers = {
        'X-Apikey': API_KEY
    }
    files = {'file': (file_path, open(file_path, 'rb'))}
    print(f'uploading {file_path}')
    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        file_id = response.json()['data']['id']
        return file_id
    else:
        print(f"Error uploading file: {response.status_code}")
        print(response.json())
        return None


def get_scan_results(file_id):
    url = f'https://www.virustotal.com/api/v3/analyses/{file_id}'
    headers = {
        'X-Apikey': API_KEY
    }
    print(url)
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result['data']['attributes']['status'] == 'completed':
                return result['data']['attributes']['results']
            else:
                print("Scan in progress, waiting for 10 seconds...")
                time.sleep(10)
        else:
            print(f"Error getting scan results: {response.status_code}")
            print(response.json())
            return None


def main():
    parser = argparse.ArgumentParser(description="Upload a file to VirusTotal and get the scan results.")
    parser.add_argument('directory', type=str, help="The path to the file to be scanned.")

    args = parser.parse_args()
    print(analyze(args.directory))
    file_id = upload_file(args.file_path)
    if file_id:
        results = get_scan_results(file_id)
        if results:
            print(results)


if __name__ == '__main__':
    main()

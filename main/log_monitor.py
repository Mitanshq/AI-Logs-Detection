import time
import os
import requests

LOG_DIR = "test_logs"
SERVER_URL = "http://127.0.0.1:5001/upload_log"

processed_files = {}  # Store {filename: last_modified_time}
# print(processed_files)

def check_for_new_logs():
    global processed_files

    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)

        if not os.path.isfile(file_path):
            continue
        
        last_modified_time = os.path.getmtime(file_path)

        # If new file or modified file, process it
        if filename not in processed_files or processed_files[filename] < last_modified_time:
            print(f"Processing new/updated log file: {filename}")
            upload_log_file(file_path)
            processed_files[filename] = last_modified_time  # Update the last modified time
            


def upload_log_file(file_path):
    """Uploads a log file to the server."""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}  # Ensure key is 'file' as expected in Flask
            response = requests.post(SERVER_URL, files=files)
            print(f"Uploaded {file_path}: {response.json()}")
    except Exception as e:
        print(f"Error uploading {file_path}: {e}")

def start_monitoring():
    """Continuously checks for new or modified log files every 60 seconds."""
    print("Starting log monitoring...")
    
    while True:
        check_for_new_logs()
        time.sleep(5)  # Wait for 5 sec before checking again

if __name__ == "__main__":
    requests.post("http://127.0.0.1:5001/upload_user")
    start_monitoring()

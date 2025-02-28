import shutil
import os
import sys
import time
import requests

def copy_files(source, destination):
    """Copy files from source to destination."""
    if not os.path.exists(source):
        print(f"Error: Source path '{source}' does not exist.")
        sys.exit(1)
    
    if os.path.exists(destination):
        print(f"Warning: Destination '{destination}' already exists. Copying contents...")
    
    try:
        shutil.copytree(source, destination, dirs_exist_ok=True)
        print("Copy operation completed.")
    except Exception as e:
        print(f"Error copying files: {e}")
        sys.exit(1)

def wait_for_upload():
    """Wait until LucidLink has uploaded all pending files."""
    cache_info_url = "http://localhost:8279/cache/info"
    while True:
        try:
            response = requests.get(cache_info_url)
            response.raise_for_status()
            data = response.json()
            dirty_bytes = data.get("dirtyBytes", 1)
            print(f"Waiting for upload... Pending bytes: {dirty_bytes}")
            
            if dirty_bytes == 0:
                break
        except requests.RequestException as e:
            print(f"Error checking upload status: {e}")
            sys.exit(1)
        time.sleep(5)

def sync_index():
    """Send a sync request to ensure file index changes are committed."""
    sync_url = "http://localhost:8279/app/sync"
    try:
        response = requests.put(sync_url)
        response.raise_for_status()
        print("File index synchronized with the cloud.")
    except requests.RequestException as e:
        print(f"Error syncing file index: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: python lucidlink_sync.py <source> <destination>")
        sys.exit(1)
    
    source = sys.argv[1]
    destination = sys.argv[2]
    
    copy_files(source, destination)
    wait_for_upload()
    sync_index()
    print("Operation completed successfully.")

if __name__ == "__main__":
    main()

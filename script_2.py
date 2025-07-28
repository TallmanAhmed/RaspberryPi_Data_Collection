import socket
import time
import os
import re
from google.cloud import storage
import sys

# ----------- INTERNET CHECK FUNCTION -----------
def check_internet(timeout=3):
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False

# ----------- CHECK INTERNET BEFORE UPLOAD -----------
print("Checking internet connection...")
if not check_internet():
    print("Internet connection not available. Exiting.")
    sys.exit(1)
else:
    print("Internet connection detected. Starting upload...")

# ----------- CLOUD UPLOAD SECTION -----------
folder_path = "/home/raspberrypi/destination"
bucket_name = "field-data-lake"

client = storage.Client()
bucket = client.bucket(bucket_name)

# Regex pattern to match expected bag filenames
pattern = re.compile(r'collection_(\d{4})-(\d{2})-(\d{2})-\d{2}-\d{2}-\d{2}\.bag$')

# Process all files in the folder
for filename in os.listdir(folder_path):
    full_path = os.path.join(folder_path, filename)

    if os.path.isfile(full_path) and filename.endswith(".bag"):
        match = pattern.match(filename)
        if match:
            year, month, day = match.groups()
            short_year = year[-2:]
            folder_name = f"{day}_{month}_{short_year}"
            blob_path = f"Field_Engineer_Dump/{folder_name}/{filename}"

            try:
                blob = bucket.blob(blob_path)
                blob.upload_from_filename(full_path)
                print(f"Uploaded: {filename} to {blob_path}")
                os.remove(full_path)
            except Exception as e:
                print(f"Failed to upload {filename}: {e}")
        else:
            print(f"Filename does not match expected pattern: {filename}")

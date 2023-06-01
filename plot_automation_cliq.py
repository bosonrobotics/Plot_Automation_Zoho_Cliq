import argparse
import os
import requests
import time
import subprocess

"""
Author: Anish Mathew Oommen P
Date: 17th February 2023

Used changeme@bosonmotors.com account
"access_token": "1000.5336464ee2bb0d45c901fb01417baeba.b381820c92baceb30f7ff942f70d3494"
refresh_token:"1000.dd659bc84874f22473fbeedc82ec0fa6.ce21261afa6e988af2bbe05644cbc54b"
client_id:"1000.16BSWJ1WR08SCSXMHTS6NMDJXBVW9F"
client_secret:"ab1e20b104c003466893d9b4010284d4b88dede857"

Anish Account Credentials
auth = ("1000.WYMFXTN7FNXCVV3FV4CVZFLBLQ2ZUJ","a88be1a0d6135ffb78a0d1b247c9da3cf9a920b936")
"refresh_token": "1000.c125a8fd026d197c896c77427a88bec6.78666ef373a12c541b0fa4a42f911514"

"""



#credential
auth = ("1000.16BSWJ1WR08SCSXMHTS6NMDJXBVW9F","ab1e20b104c003466893d9b4010284d4b88dede857")

#parameters
param = {
    "grant_type": 'refresh_token',
    "refresh_token": "1000.dd659bc84874f22473fbeedc82ec0fa6.ce21261afa6e988af2bbe05644cbc54b",
    "scope": "ZohoCliq.Webhooks.Create",
}

# Set the path to the directory containing the images
username = os.getlogin()  # Get the current user's username
dir_path =f"/home/{username}/.bags"
tokenUrl = "https://accounts.zoho.com/oauth/v2/token"

def genAccessToken():
    """generates access token from refresh token
        Args:
            None
        Returns:
            string: access token
    """   
    token = requests.post(tokenUrl, auth=auth, data=param).json()
    if 'access_token' not in token:
        raise ValueError("Access token not found in response.")
    return token['access_token'] 
    
def get_target_date():
    """
    Parses the target date from command line arguments
        Args:
            None
        Returns:
            string: target date in YYYY-MM-DD format
    """
    parser = argparse.ArgumentParser(description="Upload PNG images to Zoho Cliq channel.")
    parser.add_argument('-s',"--date", help="Target date in YYYY-MM-DD format")
    args = parser.parse_args()
    print("The Date is ",args.date)
    return args.date

# Get the target date from the command line arguments
target_date = get_target_date()

# Set the channel name and token
channel_name = "push"
token = "1000.5336464ee2bb0d45c901fb01417baeba.b381820c92baceb30f7ff942f70d3494"

# Set the API endpoint for posting messages to the channel
api_endpoint = f"https://cliq.zoho.com/api/v2/channelsbyname/{channel_name}/files"

# Set the maximum number of files to send in each batch
max_files_per_batch = 10

command =subprocess.run(["python3",dir_path+"/plot_auto_updated.py",target_date])
while True:
    # Check for internet connection
    try:
        response = requests.get('https://cliq.zoho.com')
    except requests.exceptions.ConnectionError:
        print("No internet connection. Retrying in 5 seconds...")
        time.sleep(5)
        continue

    
    
    # Get a list of all files in the directory
    files = [entry for entry in os.scandir(dir_path) if entry.name.endswith('.png') and entry.is_file() and target_date in entry.name]

    # Split the files into batches
    file_batches = [files[i:i+max_files_per_batch] for i in range(0, len(files), max_files_per_batch)]

    for file_batch in file_batches:
        # Post each image to the Cliq channel
        for entry in file_batch:
            with open(entry.path, "rb") as f:
                filename = entry.name
                files = {'file': (filename, f,'image/png')}
                headers = {'Authorization':  "Zoho-oauthtoken " + genAccessToken(),
                        }
                data = {'comments': '["Image of: ' + target_date + '"]'}

                try:
                    response = requests.post(api_endpoint, headers=headers, data=data, files=files)
                    response.raise_for_status() # raise an error if the response status code is not 2xx
                except requests.exceptions.HTTPError as error:
                    print("Error posting image to Cliq channel:", error)
                    continue
                except Exception as error:
                    print("Error:", error)
                    continue
        
        print(f"All {len(file_batch)} files uploaded successfully.")
        
        print("All files uploaded successfully.")
    break

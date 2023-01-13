# PyDrive

Script to upload a single file to a shared folder in Google Drive, then create an anchorchain.txt file for use with Jenkins

Will prompt for credentials on first run, then save the credentials to a file for future use

Syntax:
python PyDrive.py %filename% %shared_drive_id%

Must generate a credentials file in Google Cloud, using an OAuth 2.0 Client ID in the Google Drive API (can be a new or existing project)

# PyGDriveSync <sub><sup>(using Google Drive api v3)</sup></sub>
A PyGDriveSync is python module for synchronize your local file system with google drive.<br/> 
- Two way synchronize supported, which you can run any side.<br/> 
- Multi-threading are supported.

## Features
- list out files/folder by query [--query]
- google drive to local synchronization [--down_sync]
- local to google drive synchronization [--up_sync]

## Requirements
- Python 3 or higher.
- Required libraries (Mentioned in Setup-point-4)


## Setup
1. Download this project.
2. Turn on your Google Drive API (please check. [Python Quickstart](https://developers.google.com/drive/api/v3/quickstart/python))
3. Get JSON file of client secret and that file rename to "client_secrets.json" and place into current working directory. 
4. Install required libraries from [requirements.txt](requirements.txt) file.
5. run [cli.py](cli.py).
6. Enjoy

```
----------------------------------------------------------------------------------
[PyGDriveSync] using Google Drive api v3.
----------------------------------------------------------------------------------
>> Commands:
    --query q [fields]
    --down_sync drive_dir_id path [use_threads=true]
    --up_sync drive_dir_id path [use_threads=true]
----------------------------------------------------------------------------------
>> Examples:
[--query]
  --query "(not trashed) and ('root' in parents)"
  --query "(not trashed) and ('root' in parents)" "fields=id, name, kind"

[--down_sync]
--down_sync "XCDVDVCCCCC-ZZZZZZ" "C:\sync_test"
--down_sync "XCDVDVCCCCC-ZZZZZZ" "C:\sync_test" use_threads=true

[--up_sync]
--up_sync "XCDVDVCCCCC-ZZZZZZ" "C:\sync_test"
--up_sync "XCDVDVCCCCC-ZZZZZZ" "C:\sync_test" use_threads=true
----------------------------------------------------------------------------------
```
## Known issues/limitations/bugs

- you need to find drive_dir_id by your self using [--query] command.
- MimeType not used while uploading any data to google drive. it's automatically guess by google drive it self.

## Support

If you have any questions how to use this stuff, contribution or simply want to contact me, please write me on email [divyeshjagatiya@gmail.com](mailto:divyeshjagatiya@gmail.com).

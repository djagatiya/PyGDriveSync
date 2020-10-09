# PyGDriveSync <sub><sup>(using Google Drive api v3)</sup></sub>
A synchronize your local file system with google drive. A two way synchronize supported, which you can run any side.

## Features
- query
- down_sync
- up_sync (Under progress)

## Requirements
- Python 3 or higher.
- Required libraries (Mentioned in Setup-point-4)


## Setup
1. Download this project.
2. Turn on your Google Drive API (please check. [Python Quickstart](https://developers.google.com/drive/api/v3/quickstart/python))
3. Get JSON file of client secret and that file rename to "credentials.json" and place into current working directory. 
4. Install required libraries from [requirements.txt](requirements.txt) file.
5. run cli.py.
6. Enjoy

```
--------------------------------------------------------------
[PyGDriveSync] using Google Drive api v3.
--------------------------------------------------------------/--
>> Commands:
    --query q [fields]
    --down_sync drive_dir_id path [use_threads=true]
----------------------------------------------------------------
>> Examples:
[--query]
  --query "(not trashed) and ('root' in parents)"
  --query "(not trashed) and ('root' in parents)" "fields=id, name, kind"

[--down_sync]
--down_sync "XCDVDVCCCCC-ZZZZZZ" "C:\sync_test"
--down_sync "XCDVDVCCCCC-ZZZZZZ" "C:\sync_test" use_threads=true
----------------------------------------------------------------
```

## Support

If you have any questions how to use this stuff, offerings or simply want to contact me, please write me anytime on email [divyeshjagatiya@gmail.com](mailto:divyeshjagatiya@gmail.com).

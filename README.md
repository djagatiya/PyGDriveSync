# PyGDriveSync
This project for synchronize your local file system with google drive. A two way synchronize supported, which you can run any side.

---

## Features
- query
- down_sync
- up_sync (Under progress)

```
--------------------------------------------------------------
[PyGDriveSync] using Google Drive api v3.
----------------------------------------------------------------
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

---

If you have any questions how to use this stuff, offerings or simply want to contact me, please write me anytime on email [divyeshjagatiya@gmail.com](mailto:divyeshjagatiya@gmail.com).
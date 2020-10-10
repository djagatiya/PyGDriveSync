import sys
from arg_parser import SimpleArgParser
from task_runner import run_tasks
from gdrive_api import files_list, down_sync, up_sync
import time

import logging


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - [%(filename)s:%(lineno)s - %(funcName)20.20s ] %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

class LoggingCallBack:

    def __call__(self, *args, **kwargs):
        logging.info(f"{args}, {kwargs}")


def print_help():
    print("----------------------------------------------------------------------------------")
    print("[PyGDriveSync] using Google Drive api v3.")
    print("----------------------------------------------------------------------------------")
    print(">> Commands:")
    print("    --query q [fields]")
    print("    --down_sync drive_dir_id path [use_threads=true]")
    print("    --up_sync drive_dir_id path [use_threads=true]")
    print("----------------------------------------------------------------------------------")
    print(">> Examples:")
    print("[--query]")
    print("  --query \"(not trashed) and ('root' in parents)\"")
    print("  --query \"(not trashed) and ('root' in parents)\" \"fields=id, name, kind\"")
    print("")
    print("[--down_sync]")
    print("--down_sync \"XCDVDVCCCCC-ZZZZZZ\" \"C:\\sync_test\"")
    print("--down_sync \"XCDVDVCCCCC-ZZZZZZ\" \"C:\\sync_test\" use_threads=true")
    print("")
    print("[--up_sync]")
    print("--up_sync \"XCDVDVCCCCC-ZZZZZZ\" \"C:\\sync_test\"")
    print("--up_sync \"XCDVDVCCCCC-ZZZZZZ\" \"C:\\sync_test\" use_threads=true")
    print("----------------------------------------------------------------------------------")


def print_file_list(files):
    logging.info("============== QUERY ===========")
    for f in files:
        logging.info(f"{f}")


def run(command: str, args: list):
    logging.info(f"Command:{command}, Args:{args}")
    parser = SimpleArgParser(args)
    if command == '--query':
        selected_fields = parser.find_arg_by_name("fields", 'id, name')
        files = files_list(parser.find_arg(0), selected_fields=selected_fields)
        print_file_list(files)
        return

    if command == "--down_sync" or command == "--up_sync":
        drive_id = parser.find_arg(0)
        dir_path = parser.find_arg(1)

        use_threads = parser.find_arg_by_name("use_threads", "false")

        task_list = []
        if command == "--down_sync":
            down_sync(drive_id, dir_path, task_list, LoggingCallBack())
        elif command == "--up_sync":
            up_sync(dir_path, drive_id, task_list)

        if use_threads == "true":
            run_tasks(task_list)
        else:
            for func, arg in task_list:
                func(*arg)
        return

    logging.info(f"Unknown command:{command}")


def main(args: list):
    setup_logging()
    if len(args) == 0:
        print_help()
        return
    start_time = time.time()
    run(args[0], args[1:])
    time_taken = time.time() - start_time
    logging.info(f"Time Taken:{time_taken}")
    logging.info("Exit from run")


if __name__ == "__main__":
    main(sys.argv[1:])
    logging.info("Exit from main")

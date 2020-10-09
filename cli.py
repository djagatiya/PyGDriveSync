import sys
from arg_parser import SimpleArgParser
from task_runner import run_tasks
from gdrive_api import files_list, g_drive_to_local_sync


class PrintCallBack:

    def __call__(self, *args, **kwargs):
        print(*args, **kwargs)


def print_help():
    print("--------------------------------------------------------------")
    print("[PyDriveSync] using Google Drive api v3.")
    print("----------------------------------------------------------------")
    print(">> Commands:")
    print("    --query q [fields]")
    print("    --down_sync drive_dir_id path [use_threads=true]")
    print("----------------------------------------------------------------")
    print(">> Examples:")
    print("[--query]")
    print("  --query \"(not trashed) and ('root' in parents)\"")
    print("  --query \"(not trashed) and ('root' in parents)\" \"fields=id, name, kind\"")
    print("")
    print("[--down_sync]")
    print("--down_sync \"XCDVDVCCCCC-ZZZZZZ\" \"C:\\sync_test\"")
    print("--down_sync \"XCDVDVCCCCC-ZZZZZZ\" \"C:\\sync_test\" use_threads=true")
    print("----------------------------------------------------------------")


def print_file_list(files):
    print("============== QUERY ===========")
    for f in files:
        print(f)


def run(command: str, args: list):
    print("Command:", command, "Args:", args)
    parser = SimpleArgParser(args)
    if command == '--query':
        selected_fields = parser.find_arg_by_name("fields", 'id, name')
        files = files_list(parser.find_arg(0), selected_fields=selected_fields)
        print_file_list(files)
    elif command == "--down_sync":
        drive_id = parser.find_arg(0)
        dir_path = parser.find_arg(1)
        use_threads = parser.find_arg_by_name("use_threads", "false")
        task_list = [(func, arg) for func, arg in g_drive_to_local_sync(drive_id, dir_path, PrintCallBack())]
        if use_threads == "true":
            run_tasks(task_list)
        else:
            for func, arg in task_list:
                func(*arg)
    elif command == "--up_sync":
        print("This operation is under progress....")
    else:
        print("Unknown command:" + command)


def main(args: list):
    if len(args) == 0:
        print_help()
        return
    run(args[0], args[1:])
    print("Exit from run")


if __name__ == "__main__":
    main(sys.argv[1:])
    print("Exit from main")

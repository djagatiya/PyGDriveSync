import ctypes
import threading
from collections import deque
from time import sleep


class ThreadWithException(threading.Thread):

    def raise_exception(self, exception):
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.ident),
                                                         ctypes.py_object(exception))
        if res != 1:
            raise SystemError("PyThreadState_SetAsyncExc failed to raise Exception.")


class Worker(ThreadWithException):

    def __init__(self, queue: deque, lock: threading.Lock):
        super().__init__()
        self.lock = lock
        self.queue = queue
        self.start()

    def run(self):
        while 1:
            r = None
            self.lock.acquire()
            if len(self.queue) > 0:
                r = self.queue.popleft()
            self.lock.release()
            if r is None:
                continue

            if r[0] is None and r[1] == "EXIT":
                break
            else:
                r[0](*r[1])


class TaskRunner:

    def __init__(self, worker=3) -> None:
        self.deque = deque()
        self.lock = threading.Lock()
        self.workers = [Worker(self.deque, self.lock) for _ in range(worker)]

    def add(self, func, args):
        self.lock.acquire()
        self.deque.append((func, args))
        self.lock.release()

    def raise_exc(self):
        for w in self.workers:
            if w.is_alive():
                w.raise_exception(KeyboardInterrupt)

    def clear(self):
        self.lock.acquire()
        self.deque.clear()
        self.lock.release()

    def queue_len(self):
        self.lock.acquire()
        len_queue = len(self.deque)
        self.lock.release()
        return len_queue

    def shutdown(self):
        for _ in self.workers:
            self.add(None, "EXIT")
        # for w in self.workers:
        #     w.join()


def run_tasks(task_list, workers=3):
    """
    Writing own thread executor.
    for
        1: exiting when press [ctrl + c].
            - stop all workers and pool it self.
    we have used "ctypes.pythonapi.PyThreadState_SetAsyncExc" for stopping current running thread.
    :param workers:
    :param task_list:
    :return:
    """
    runner = TaskRunner(worker=workers)
    try:
        for fn, arg in task_list:
            print(fn, arg)
            runner.add(func=fn, args=arg)
        runner.shutdown()
        while runner.queue_len() > 0:
            sleep(0.1)
    except KeyboardInterrupt:
        print("KeyboardInterrupt error received...")
        runner.raise_exc()

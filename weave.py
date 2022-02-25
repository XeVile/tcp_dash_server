import threading

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        self._stop_event = threading.Event()
        self._print_lock = threading.Lock()

    def assign(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
    
    ## UNUSED FOR ASSIGNMENT
    def lock(self, lock):
        if lock == True:
            self._print_lock.acquire()
        elif lock == False:
            self._print_lock.release()
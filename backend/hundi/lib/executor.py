import logging
from threading import Event, RLock, Thread

logger = logging.getLogger(__name__)


class ExecutorLib(object):

    def __init__(self, cancellable):
        self._cancellable = cancellable
        self._thread_lock = RLock()
        self._scheduled_action = None
        self._scheduled_action_lock = RLock()
        self._is_cancelled = False
        self._finish_event = Event()

    @property
    def busy(self):
        return self.scheduled_action is not None

    def schedule(self, action):
        with self._scheduled_action_lock:
            if self._scheduled_action is not None:
                return self._scheduled_action
            self._scheduled_action = action
            self._is_cancelled = False
            self._finish_event.set()
        return None

    @property
    def scheduled_action(self):
        with self._scheduled_action_lock:
            return self._scheduled_action

    def reset_scheduled_action(self):
        with self._scheduled_action_lock:
            self._scheduled_action = None

    def run_async(self, func, args=()):
        Thread(target=self.run, args=(func, args)).start()

    def try_run_async(self, action, func, args=()):
        prev = self.schedule(action)
        if prev is None:
            return self.run_async(func, args)
        raise RuntimeError('Failed to run {0}, {1} is already in progress'.format(action, prev))

    def cancel(self):
        with self:
            with self._scheduled_action_lock:
                if self._scheduled_action is None:
                    return
                logger.warning('Cancelling long running task %s', self._scheduled_action)
            self._is_cancelled = True

        self._cancellable.cancel()
        self._finish_event.wait()

        with self:
            self.reset_scheduled_action()

    def __enter__(self):
        self._thread_lock.acquire()

    def __exit__(self, *args):
        self._thread_lock.release()

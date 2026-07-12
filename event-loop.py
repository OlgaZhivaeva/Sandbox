# ---------------------- код Бизли --------- эхо сервер -----------------------------
import logging
import sys
import types
from typing import Generator, Union
from queue import Queue
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from socket import socket, AF_INET, SOCK_STREAM
from typing import Tuple


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class Task:
    task_id = 0

    def __init__(self, target: Generator):
        Task.task_id += 1
        self.tid = Task.task_id  # Task ID
        self.target = target  # Target coroutine
        self.sendval = None  # Value to send
        self.stack = []  # Call stack

    # Run a task until it hits the next yield statement
    def run(self):
        while True:
            try:
                result = self.target.send(self.sendval)
                if isinstance(result, SystemCall):
                    return result

                if isinstance(result, types.GeneratorType):
                    self.stack.append(self.target)
                    self.sendval = None
                    self.target = result
                else:
                    if not self.stack:
                        return
                    self.sendval = result
                    self.target = self.stack.pop()

            except StopIteration:
                if not self.stack:
                    raise
                self.sendval = None
                self.target = self.stack.pop()


class Scheduler:
    def __init__(self):
        self.ready = Queue()
        self.selector = DefaultSelector()
        self.task_map = {}

    def add_task(self, coroutine: Generator) -> int:
        new_task = Task(coroutine)
        self.task_map[new_task.tid] = new_task
        self.schedule(new_task)
        return new_task.tid

    def exit(self, task: Task):
        logger.info('Task %d terminated', task.tid)
        del self.task_map[task.tid]

    # I/O waiting
    def wait_for_read(self, task: Task, fd: int):
        try:
            key = self.selector.get_key(fd)
        except KeyError:
            self.selector.register(fd, EVENT_READ, (task, None))

        else:
            mask, (reader, writer) = key.events, key.data
            self.selector.modify(fd, mask | EVENT_READ, (task, writer))

    def wait_for_write(self, task: Task, fd: int):
        try:
            key = self.selector.get_key(fd)
        except KeyError:
            self.selector.register(fd, EVENT_WRITE, (None, task))

        else:
            mask, (reader, writer) = key.events, key.data
            self.selector.modify(fd, mask | EVENT_WRITE, (reader, task))

    def _remove_reader(self, fd: int):
        try:
            key = self.selector.get_key(fd)
        except KeyError:
            pass
        else:
            mask, (reader, writer) = key.events, key.data
            mask &= ~EVENT_READ
            if not mask:
                self.selector.unregister(fd)
            else:
                self.selector.modify(fd, mask, (None, writer))

    def _remove_writer(self, fd: int):
        try:
            key = self.selector.get_key(fd)
        except KeyError:
            pass
        else:
            mask, (reader, writer) = key.events, key.data
            mask &= ~EVENT_WRITE
            if not mask:
                self.selector.unregister(fd)
            else:
                self.selector.modify(fd, mask, (reader, None))

    def io_poll(self, timeout: Union[None, float]):
        if not self.selector.get_map():
            return
        events = self.selector.select(timeout)
        for key, mask in events:
            fileobj, (reader, writer) = key.fileobj, key.data
            if mask & EVENT_READ and reader is not None:
                self.schedule(reader)
                self._remove_reader(fileobj)
            if mask & EVENT_WRITE and writer is not None:
                self.schedule(writer)
                self._remove_writer(fileobj)

    def io_task(self) -> Generator:
        while True:
            if self.ready.empty():
                self.io_poll(None)
            else:
                self.io_poll(0)
            yield


    def schedule(self, task: Task):
        self.ready.put(task)

    def _run_once(self):
        task = self.ready.get()
        try:
            result = task.run()
            if isinstance(result, SystemCall):
                result.handle(self, task)
                return
        except StopIteration:
            self.exit(task)
            return
        self.schedule(task)

    def event_loop(self):
        self.add_task(self.io_task())
        while self.task_map:
            self._run_once()


class SystemCall:
    def handle(self, sched: Scheduler, task: Task):
        pass


class NewTask(SystemCall):
    def __init__(self, target: Generator):
        self.target = target

    def handle(self, sched: Scheduler, task: Task):
        tid = sched.add_task(self.target)
        task.sendval = tid
        sched.schedule(task)


class WriteWait(SystemCall):
    def __init__(self, f):
        self.f = f

    def handle(self, sched, task):
        fd = self.f.fileno()
        sched.wait_for_write(task, fd)


# Wait for reading
class ReadWait(SystemCall):
    def __init__(self, f):
        self.f = f

    def handle(self, sched, task):
        fd = self.f.fileno()
        sched.wait_for_read(task, fd)


class AsyncSocket:
    def __init__(self, sock: socket):
        self.sock = sock

    def accept(self) -> Tuple['AsyncSocket', str]:
        yield ReadWait(self.sock)
        client, addr = self.sock.accept()
        return AsyncSocket(client), addr

    def send(self, buffer: bytes):
        while buffer:
            yield WriteWait(self.sock)
            len = self.sock.send(buffer)
            buffer = buffer[len:]

    def recv(self, maxbytes: int) -> bytes:
        yield ReadWait(self.sock)
        return self.sock.recv(maxbytes)

    def close(self):
        yield self.sock.close()


def handle_client(client, addr):
    print("Connection from", addr)
    while True:
        data = yield from client.recv(65536)
        if not data:
            break
        yield from client.send(data)
    print("Client closed")
    client.close()


def server(port):
    print("Server starting")
    rawsock = socket(AF_INET, SOCK_STREAM)
    rawsock.bind(("", port))
    rawsock.listen()
    sock = AsyncSocket(rawsock)
    try:
        while True:
            client, addr = yield from sock.accept()
            yield NewTask(handle_client(client, addr))
    finally:
        sock.close()


if __name__ == '__main__':
    shed = Scheduler()
    shed.add_task(server(8000))
    shed.event_loop()

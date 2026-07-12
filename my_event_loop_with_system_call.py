import logging
import select
import socket
import sys
import time
from typing import Generator


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class Task:
    task_id = 0
    def __init__(self, coro: Generator):
        self.coro = coro
        Task.task_id += 1
        self.tid = Task.task_id
        self.sendval = None


    def run(self):
        val = self.sendval
        self.sendval = None
        return self.coro.send(val)


class EventLoop:
    def __init__(self):
        self.tasks = []            # очередь для задач
        self.sleeping_tasks = [] # очередь для спящих задач
        self.reading_sockets = [] # очередь для задач ждущих ввода

    def add_task(self, task):
        new_task = Task(task)
        self.tasks.append(new_task)
        logger.info(f"Добавлена задача: {new_task.tid}")

    def run_task(self):
        if not self.tasks: # добавлено из-за особенностей ос windows
            return
        task = self.tasks.pop(0) # удаляем задачу из начала очереди
        try:
            logger.info(f"Запускаем шаг задачи: {task.tid}")
            result = task.run() # пробуем запустить задачу (в ответ можем получить корутину или StopIteration)
            if isinstance(result, SystemCall):
                result.handle(self, task) # если это системный вызов выполняем метод handle
            else:
                self.tasks.append(task) # если это не системный вызов и нет StopIteration ставим задачу в конец очереди
        except StopIteration:
            logger.info(f"Задача {task.tid} завершилась.")

    def start(self):
        logger.info("Цикл событий запущен.")
        while self.tasks or self.sleeping_tasks or self.reading_sockets: # цикл событий будет крутиться, пока есть задачи.
            if self.tasks:
                self.run_task()

            if self.sleeping_tasks:
                first_task, wake_time = self.sleeping_tasks.pop(0)
                now = time.time()

                if now < wake_time:
                    self.sleeping_tasks.append((first_task, wake_time))
                    if not self.tasks: # чтобы не перегружать процессор
                        time.sleep(0.1)
                else:
                    logger.info(f"Задача {first_task.tid} перенесена из ожидания в активную очередь.")
                    self.tasks.append(first_task)

            if self.reading_sockets:
                sockets_to_poll = [sock for sock, task in self.reading_sockets]  # собираем список только сокетов для передачи в select

                ready, _, _ = select.select(sockets_to_poll, [], [], 0)

                for ready_sock in ready:
                    for sock, task in list(self.reading_sockets):
                        if sock is ready_sock:
                            self.reading_sockets.remove((sock, task))

                            data = ready_sock.recv(1024) # читаем данные из сокета

                            task.sendval = data # передаем данные внутрь задачи и возвращаем её в очередь активных
                            self.tasks.append(task)
                            logger.info(f"Данные из сокета получены. Возвращаем задачу {task.tid} в очередь.")

        logger.info("Цикл событий завершен. Задач больше нет.")


class SystemCall:
    def handle(self, loop: EventLoop, task: Task):
        pass


class AsyncSleep(SystemCall):
    def __init__(self, seconds):
        self.seconds = seconds

    def handle(self, loop, task):
        wake_time = time.time() + self.seconds
        loop.sleeping_tasks.append((task, wake_time))
        logger.info(f"Задача {task.tid} отправлена спать на {self.seconds} сек.")


class ReadSocket(SystemCall):
    def __init__(self, sock):
        self.sock = sock

    def handle(self, loop: EventLoop, task: Task):
        loop.reading_sockets.append((self.sock, task))
        logger.info(f"Задача {task.tid} ожидает данные из сокета...")


# --- ПРОВЕРКА ---

def task_a():
    for i in range(3):
        print(f"  [Задача A]  Шаг {i}")
        yield

def task_b():
    for i in range(3):
        print(f"  [Задача B]  Шаг {i}")
        yield

def task_c():
    print("  [Задача C] Начало")
    yield AsyncSleep(3)
    print("  [Задача C] Проснулась и продолжила работу!")

def task_socket_to_file(client_sock):
    with open("output.txt", "a", encoding="utf-8") as f:
        print("Ожидаем сообщение от клиента для записи в файл...")

        data = yield ReadSocket(client_sock)

        text = data.decode('utf-8', errors='ignore').strip()
        f.write(text + "\n")
        print(f"Записано в файл: {text}")

    client_sock.close()
    print("Сокет закрыт.")



if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Создаем слушающий сокет
    server.bind(("127.0.0.1", 9000))
    server.listen(1)
    print("Запусти telnet 127.0.0.1 9000 во втором терминале...")
    client_sock, addr = server.accept()
    print(f"Клиент подключился: {addr}")

    loop = EventLoop()
    loop.add_task(task_a())
    loop.add_task(task_b())
    loop.add_task(task_c())

    loop.add_task(task_socket_to_file(client_sock))

    loop.start()
    server.close()

import logging
import sys
import time
from typing import Generator, Tuple


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class Task:
    task_id = 0
    def __init__(self, coro: Generator):
        self.coro = coro
        Task.task_id += 1
        self.tid = Task.task_id

    def run(self):
        return self.coro.send(None)


class EventLoop:
    def __init__(self):
        self.tasks = []            # очередь для задач
        self.waiting_for_read = [] # очередь для SistemCall задач

    def add_task(self, task):
        new_task = Task(task)
        self.tasks.append(new_task)
        logger.info(f"Добавлена задача: {new_task.tid}")

    def run_task(self):
        if not self.tasks:
            return
        task = self.tasks.pop(0)
        try:
            logger.info(f"Запускаем шаг задачи: {task.tid}")
            result = task.run()
            if isinstance(result, SystemCall):
                result.handle(self, task)
            else:
                self.tasks.append(task)
        except StopIteration:
            logger.info(f"Задача {task.tid} завершилась.")


    def start(self):
        logger.info("Цикл событий запущен.")
        while self.tasks or self.waiting_for_read:
            if self.tasks:
                self.run_task()

            if self.waiting_for_read:
                first_task, wake_time = self.waiting_for_read.pop(0)
                now = time.time()

                if now < wake_time:
                    self.waiting_for_read.append((first_task, wake_time))
                    if not self.tasks:
                        time.sleep(0.1)
                else:
                    logger.info(f"Задача {first_task.tid} перенесена из ожидания в активную очередь.")
                    self.tasks.append(first_task)

        logger.info("Цикл событий завершен. Задач больше нет.")

class SystemCall:
    def handle(self, loop: EventLoop, task: Task):
        pass


class AsyncSleep(SystemCall):
    def __init__(self, seconds):
        self.seconds = seconds

    def handle(self, loop, task):
        wake_time = time.time() + self.seconds
        loop.waiting_for_read.append((task, wake_time))
        logger.info(f"Задача {task.tid} отправлена спать на {self.seconds} сек.")


# --- ПРОВЕРКА ---

def task_a():
    for i in range(3):
        print(f"Задача A  Шаг {i}")
        yield

def task_b():
    for i in range(3):
        print(f"Задача B  Шаг {i}")
        yield

def task_c():
    print("  [Задача C] Начало")
    yield AsyncSleep(5)
    print("  [Задача C] Проснулась и продолжила работу!")

def task_d():
    print("  [Задача D] Начало")
    yield AsyncSleep(3)
    print("  [Задача D] Проснулась и продолжила работу!")



if __name__ == "__main__":
    loop = EventLoop()
    loop.add_task(task_a())
    loop.add_task(task_b())
    loop.add_task(task_c())
    loop.add_task(task_d())
    loop.start()

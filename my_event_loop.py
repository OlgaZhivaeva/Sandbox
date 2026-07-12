# ---------- Примитивный цикл событий ---- Задачи не могут быть вложенными -------
import logging
import sys
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

    def run(self):
        return next(self.coro)


class EventLoop:
    def __init__(self):
        self.tasks = []


    def add_task(self, task):
        new_task = Task(task)
        self.tasks.append(new_task)
        logger.info(f"Добавлена задача: {new_task.tid}")


    def run_task(self):
        if not self.tasks:
            return
        task = self.tasks.pop(0)
        try:
            logger.info(f"Выполняется задача: {task.tid}")
            task.run()
            self.tasks.append(task)
        except StopIteration as e:

            logger.info(f"Исключение: {type(e).__name__}. Задача {task.tid} удалена.")


    def start(self):
        logger.info("Цикл событий запущен.")
        while self.tasks:
            self.run_task()
        logger.info("Цикл событий завершен. Задач больше нет.")


# --- ПРОВЕРКА ---

def task_a():
    for i in range(3):
        print(f"  [Задача A]  Шаг {i}")
        yield


def task_b():
    for i in range(3):
        print(f"  [Задача B]  Шаг {i}")
        yield


if __name__ == "__main__":
    loop = EventLoop()
    loop.add_task(task_a())
    loop.add_task(task_b())
    loop.start()

class Task:
    def __init__(self, coro):
        self.coro = coro

    def run(self):
        return next(self.coro)


class EventLoop:
    def __init__(self):
        self.tasks = []

    def add_task(self, coro):
        new_task = Task(coro)
        self.tasks.append(new_task)

    def start(self):
        print("Цикл событий запущен.")

        while self.tasks:
            task = self.tasks.pop(0)
            try:
                print("Выполняется загрузка...")
                task.run()
                self.tasks.append(task)
            except StopIteration:
                print("Загрузка файла завершена")

        print("Цикл событий завершен. Все файлы скачаны!")


# --- Функция-генератор для симуляции загрузки ---
def download_file(filename: str, total_mb: int):

    for current_mb in range(1, total_mb + 1):
        print(f"  [{filename}] Скачано {current_mb}/{total_mb} МБ...")
        yield



if __name__ == "__main__":
    loop = EventLoop()

    # Добавляем три задачи загрузки
    loop.add_task(download_file("Файл А", 3))
    loop.add_task(download_file("Файл B", 5))
    loop.add_task(download_file("Файл C", 2))

    loop.start()

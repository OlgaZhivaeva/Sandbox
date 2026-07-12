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
                task.run()
                self.tasks.append(task)
            except StopIteration:
                pass
        print("Цикл событий завершен. Все отчеты распечатаны!")


# --- АСИНХРОННАЯ ЗАДАЧА ---

def employee(name: str, total_pages: int, printer: dict):
    """
    Сотрудник пытается распечатать total_pages страниц на принтере.
    """
    while True:
        if printer["locked_by"] != name and printer["locked_by"] is not None:
            print(f"  [{name}] Принтер занят сотрудником {printer['locked_by']}. Жду...")
            yield
            continue
        if printer["locked_by"] is None:
            printer["locked_by"] = name
            print(f"  [{name}] Принтер свободен! Занимаю принтер.")
            break
    for page in range(1, total_pages + 1):
        print(f"  [{name}] Печатаю страницу {page} из {total_pages}...")
        yield
    printer["locked_by"] = None
    print(f"  [{name}] Печать закончена. Освобождаю принтер!")


if __name__ == "__main__":
    loop = EventLoop()

    # Общий принтер
    shared_printer = {"locked_by": None}

    # Добавляем трех сотрудников, каждому нужно распечатать по 3 страницы
    loop.add_task(employee("Алиса", 3, shared_printer))
    loop.add_task(employee("Боб", 3, shared_printer))
    loop.add_task(employee("Чарли", 3, shared_printer))

    loop.start()

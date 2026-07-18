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
        print("Цикл событий завершен. Все пиццы доставлены!")


# --- АСИНХРОННЫЕ ЗАДАЧИ ---

def baker(name: str, total_pizzas: int, plate: list):
    """
    Пекарь готовит пиццы одну за другой.
    Максимум на тарелке (plate) может быть 2 пиццы.
    """
    pizza_number = 1
    while pizza_number <= total_pizzas:

        if len(plate) >= 2:
            print(f"  [{name}] Тарелка полна! Жду курьера...")
            yield
            continue

        plate.append(f"Пицца №{pizza_number}")
        print(f"  [{name}] Испек пиццу №{pizza_number}. На тарелке: {len(plate)}")
        pizza_number += 1
        yield


def courier(name: str, total_pizzas: int, plate: list):
    """
    Курьер забирает пиццы с тарелки и доставляет их.
    Всего ему нужно доставить total_pizzas.
    """
    delivered = 0
    while delivered < total_pizzas:

        if len(plate) == 0:
            print(f"  [{name}] Нет пиццы! Жду пекаря...")
            yield
            continue
        plate.pop(0)
        delivered += 1
        print(f"  [{name}] Забрал пиццу №{delivered}. На тарелке: {len(plate)}")
        yield


# --- Точка входа ---
if __name__ == "__main__":
    loop = EventLoop()
    shared_plate = []

    # Добавляем ДВУХ пекарей (каждый должен испечь по 3 пиццы, всего 6)
    loop.add_task(baker("Пекарь Марио", 3, shared_plate))
    loop.add_task(baker("Пекарь Луиджи", 3, shared_plate))

    # И одного курьера (он должен доставить все 6 пицц)
    loop.add_task(courier("Курьер Тони", 6, shared_plate))

    loop.start()

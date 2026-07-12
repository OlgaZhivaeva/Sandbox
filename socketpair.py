import multiprocessing
import os
import socket


def child_worker(child_sock):
    # Дочерний процесс получает сообщение
    msg = child_sock.recv(1024).decode()
    print(f"[Child {os.getpid()}] Получено: {msg}")

    # Отправляет ответ
    child_sock.sendall("Привет от потомка!".encode("utf-8"))
    child_sock.close()


if __name__ == "__main__":
    # Создаем пару соединенных сокетов (по умолчанию AF_UNIX на Linux/macOS)
    parent_sock, child_sock = socket.socketpair()

    # Запускаем дочерний процесс и передаем ему его конец сокета
    p = multiprocessing.Process(target=child_worker, args=(child_sock,))
    p.start()

    # Родитель закрывает ненужный ему в этом потоке сокет потомка
    child_sock.close()

    # Родитель отправляет данные
    parent_sock.sendall("Привет от родителя!".encode("utf-8"))

    # Получает ответ
    response = parent_sock.recv(1024).decode()
    print(f"[Parent] Ответ: {response}")

    parent_sock.close()
    p.join()

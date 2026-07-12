import selectors
import sockets

selector = selectors.DefaultSelector()


def accept_wrapper(sock):
    conn, addr = sock.accept()
    conn.setblocking(False)  # Важно!
    # Регистрируем клиентский сокет на событие чтения (READ)
    # и привязываем к нему callback `read_wrapper`
    selector.register(conn, selectors.EVENT_READ, data=read_wrapper)


def read_wrapper(conn):
    data = conn.recv(1024)
    if data:
        conn.sendall(data)  # Эхо-сервер
    else:
        # Клиент закрыл соединение
        selector.unregister(conn)
        conn.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("localhost", 8080))
server.listen()
server.setblocking(False)

# Регистрируем серверный сокет на чтение (входящие подключения)
selector.register(server, selectors.EVENT_READ, data=accept_wrapper)

# Наш собственный Event Loop
while True:
    events = selector.select(timeout=None)  # Блокируется, пока нет событий
    for key, mask in events:
        callback = key.data
        callback(key.fileobj)  # Вызываем callback, передавая туда сокет

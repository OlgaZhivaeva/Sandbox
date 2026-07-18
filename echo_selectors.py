# echo_selectors.py
import selectors
import socket

sel = selectors.DefaultSelector()   # сам выберет лучший механизм ОС

def accept(srv):
    """Событие на слушающем сокете = новый клиент"""
    conn, addr = srv.accept()
    print('Подключился', addr)
    conn.setblocking(False)                          # не блокировать!
    sel.register(conn, selectors.EVENT_READ, read)   # следи и за ним

def read(conn):
    """Событие на сокете клиента = пришли данные (или клиент ушёл)"""
    data = conn.recv(1024)
    if data:
        conn.sendall(data)          # эхо
    else:
        print('Клиент отключился')
        sel.unregister(conn)        # убрать лампочку с табло
        conn.close()

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('127.0.0.1', 8000))
srv.listen()
srv.setblocking(False)
sel.register(srv, selectors.EVENT_READ, accept)
print('Слушаю 127.0.0.1:8000 ...')

while True:                         # ← ЦИКЛ СОБЫТИЙ
    events = sel.select()           # ← 😴 ждём ОДИН раз ЗА ВСЕХ
    for key, mask in events:
        callback = key.data         # это accept или read
        callback(key.fileobj)       # key.fileobj — сокет, где событие

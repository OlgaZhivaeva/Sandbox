import socket

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IPv4, SOCK_STREAM = TCP
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('127.0.0.1', 8000))   # занять адрес
srv.listen()                    # слушать
print('Слушаю 127.0.0.1:8000 ...')

while True:
    conn, addr = srv.accept()   # ⏳ БЛОКИРУЕТСЯ: ждём, пока кто-то позвонит
    print('Подключился', addr)
    while True:
        data = conn.recv(1024)  # ⏳ БЛОКИРУЕТСЯ: ждём, пока клиент что-то пришлёт
        if not data:            # пустые байты = клиент положил трубку
            break
        conn.sendall(data)      # эхо: отправляем то же самое обратно
    conn.close()
    print('Отключился', addr)



# import socket
#
# srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IPv4, SOCK_STREAM = TCP
# srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# srv.bind(('127.0.0.1', 8000))   # занять адрес
# srv.listen()                    # слушать
# print('Слушаю 127.0.0.1:8000 ...')
#
# while True:
#     conn, addr = srv.accept()   # ⏳ БЛОКИРУЕТСЯ: ждём, пока кто-то позвонит
#     print('conn:', conn)
#     print('Подключился', addr)
#     rfile = conn.makefile('r', encoding='utf-8')
#     wfile = conn.makefile('w', encoding='utf-8')
#     while True:
#         data = rfile.readline()
#         if not data:            # пустые байты = клиент положил трубку
#             break
#         wfile.write(data)
#         wfile.flush()
#         print(data.strip())
#     rfile.close()
#     wfile.close()
#     conn.close()
#     print('Отключился', addr)

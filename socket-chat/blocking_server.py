import socket


def blocking_server():
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv_sock.bind(('127.0.0.1', 8000))
    serv_sock.listen()
    print('Сервер слушает 127.0.0.1:8000...')
    while True:
        conn, addr = serv_sock.accept()
        print(f'Подключился клиент {addr}')
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.send(data)
        print(f'Клиент {addr} отключился')
        conn.close()



if __name__ == '__main__':
    blocking_server()

import socket
import threading


def handle_client(conn, addr):
    print(f'[НОВЫЙ ПОТОК] Запущен для {addr}')

    rfile = conn.makefile('r', encoding='utf-8', errors='replace')
    wfile = conn.makefile('w', encoding='utf-8')

    try:
        while True:
            line = rfile.readline()
            if not line:
                break
            print(f'[{addr[1]}]: {line.strip()}')

            wfile.write(line)
            wfile.flush()
    except ConnectionError as e:
        print(f'[{addr[1]}] Произошла ошибка: {e}')
    finally:
        rfile.close()
        wfile.close()
        conn.close()
        print(f'Отключился {addr}')


if __name__ == '__main__':
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('127.0.0.1', 8000))
    srv.listen()
    print('Слушаю 127.0.0.1:8000 ...')

    # Главный цикл сервера (Главный поток)
    while True:
        conn, addr = srv.accept()  # Ждем подключения (блокируется только главный поток)
        print('Подключился', addr)

        client_thread = threading.Thread(target=handle_client, args=(conn, addr))

        client_thread.daemon = True

        client_thread.start()

import socket
import threading

# Словарь для хранения активных клиентов: {адрес: wfile_объект}
clients = {}
# Блокировка для безопасного доступа к словарю из разных потоков
clients_lock = threading.Lock()


def broadcast(message, sender_addr):
    """Отправляет сообщение всем подключенным клиентам, кроме отправителя"""
    with clients_lock:  # Безопасно входим в список клиентов
        for addr, wfile in clients.items():
            if addr != sender_addr:  # Не отправляем автору сообщения его же текст
                try:
                    wfile.write(message)
                    wfile.flush()

                except ConnectionError:
                    # Если отправить не удалось (клиент "отвалился"), мы его проигнорируем.
                    # Он будет удален в своем собственном потоке handle_client.
                    pass


def handle_client(conn, addr):
    print(f'[НОВЫЙ ПОТОК] Запущен для {addr}')

    rfile = conn.makefile('r', encoding='utf-8', errors='replace')
    wfile = conn.makefile('w', encoding='utf-8')

    # Регистрируем нового клиента в общем списке
    with clients_lock:
        clients[addr] = wfile

    # Оповещаем всех, что вошел новый участник
    broadcast(f' New user {addr[1]} has joined\n', addr)

    try:
        wfile.write(f"Welcome to the chat! Your port: {addr[1]}\n")
        wfile.flush()

        while True:
            line = rfile.readline()
            if not line:
                break

            # Сообщение, которое мы разошлем остальным
            message = f'\n[{addr[1]}]: {line}'
            print(message.strip())  # Вывод в консоль сервера

            # Передаем сообщение во все остальные потоки клиентов
            broadcast(message, addr)

    except ConnectionError as e:
        print(f'[{addr[1]}] Произошла ошибка: {e}')
    finally:
        # Удаляем клиента из списка при отключении
        with clients_lock:
            if addr in clients:
                del clients[addr]

        rfile.close()
        wfile.close()
        conn.close()
        print(f'Disconnected {addr}')

        # Оповещаем всех, что участник вышел
        broadcast(f'Пользователь {addr[1]} покинул чат\n', addr)


if __name__ == '__main__':
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('127.0.0.1', 8000))
    srv.listen()
    print('Чат-сервер запущен на 127.0.0.1:8000 ...')

    while True:
        conn, addr = srv.accept()
        print('Подключился', addr)

        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()
